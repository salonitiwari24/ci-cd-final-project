#!/bin/bash
set -e

echo "=========================================================="
echo " Starting OpenShift Pipeline & Application Verification"
echo "=========================================================="

echo "=== 1. Inspecting User & Active Namespace ==="
oc whoami
CURRENT_NS=$(oc project -q)
echo "Active Project: $CURRENT_NS"

echo "=== 2. Creating / Verifying PersistentVolumeClaim ==="
oc apply -f tekton/pvc.yaml
oc get pvc pipelinerun-pvc

echo "=== 3. Installing Custom Tekton Tasks (cleanup & nose) ==="
oc apply -f tekton/tasks.yaml
oc get tasks

echo "=== 4. Applying Tekton CD Pipeline (cd-pipeline) ==="
oc apply -f tekton/pipeline.yaml
oc get pipeline cd-pipeline

echo "=== 5. Running the Pipeline ==="
echo "Starting PipelineRun with shared workspace bound to pipelinerun-pvc..."
tkn pipeline start cd-pipeline \
  -w name=pipeline-workspace,claimName=pipelinerun-pvc \
  -p repo-url="https://github.com/salonitiwari24/ci-cd-final-project.git" \
  -p branch="main" \
  --showlog

echo "=== 6. Capturing PipelineRun Logs to pipelinerun.txt ==="
mkdir -p submission_evidence
tkn pipelinerun logs -L | tee pipelinerun.txt
cp pipelinerun.txt submission_evidence/pipelinerun.txt

echo "=== 7. Checking Application Rollout ==="
oc rollout status deployment/hit-counter --timeout=180s
oc get pods -l app=hit-counter

echo "=== 8. Capturing Application Logs to Evidence File ==="
oc logs deployment/hit-counter | tee submission_evidence/oc-pipeline-app-logs
cp submission_evidence/oc-pipeline-app-logs ./oc-pipeline-app-logs
cp submission_evidence/oc-pipeline-app-logs ./oc-pipeline-application-logs

echo "=========================================================="
echo " Pipeline execution and verification completed successfully!"
echo " Logs written to pipelinerun.txt and oc-pipeline-app-logs"
echo "=========================================================="
