# CI/CD Tools and Practices Final Project — Continuous Delivery with Tekton & OpenShift

## Project Information

- **Student Name / GitHub Account:** `salonitiwari24`
- **Repository:** [https://github.com/salonitiwari24/ci-cd-final-project](https://github.com/salonitiwari24/ci-cd-final-project)
- **Course:** Continuous Integration and Continuous Delivery (CI/CD) / DevOps Capstone — IBM Skills Network
- **Application:** Cloud-Native Python Flask Hit Counter Microservice (`service/`)

---

## Executive Summary

This repository contains the complete implementation for **Option 1: AI-Graded Submission and Evaluation** of the IBM Skills Network CI/CD Final Project. It implements:
1. **Continuous Integration (CI):** An automated GitHub Actions pipeline validating code style with `flake8` and executing the `nose` unit test suite with 100% test coverage inside a containerized Python 3.9 runtime.
2. **Continuous Delivery (CD):** A cloud-native Tekton pipeline orchestrating 6 sequential delivery stages on Red Hat OpenShift: workspace cleanup, git checkout, flake8 linting, nosetests execution, rootless container image building with `buildah`, and container deployment to the OpenShift cluster using `openshift-client`.

---

## Repository Structure

```
├── .github/
│   └── workflows/
│       ├── README.md
│       └── workflow.yml                 # Automated GitHub Actions CI workflow
├── .tekton/
│   ├── README.md
│   ├── tasks.yml                        # Tekton custom tasks (cleanup, nose)
│   ├── pipeline.yml                     # 6-stage Tekton CD Pipeline
│   ├── pvc.yml                          # PersistentVolumeClaim definition
│   └── pipelinerun.yml                  # PipelineRun trigger definition
├── tekton/
│   ├── tasks.yaml                       # Tekton tasks (catalog & custom)
│   ├── pipeline.yaml                    # CD Pipeline definition (lab-standard)
│   ├── pvc.yaml                         # PVC for pipeline workspace
│   └── pipelinerun.yaml                 # PipelineRun trigger
├── deploy/
│   ├── deployment.yaml                  # OpenShift deployment manifest with image placeholder
│   ├── service.yaml                     # ClusterIP service for port 8000
│   └── route.yaml                       # OpenShift Route for external access
├── bin/
│   ├── setup.sh                         # Environment setup script
│   └── run_openshift_pipeline.sh        # Automated pipeline executor & evidence collector
├── service/                             # Python Flask microservice
│   ├── __init__.py                      # Application initializer & logging setup
│   ├── routes.py                        # REST API endpoint handlers (/health, /counters)
│   └── common/
│       ├── error_handlers.py            # HTTP error response formatters
│       ├── log_handlers.py              # Log handler configuration
│       └── status.py                    # HTTP status code constants
├── tests/
│   └── test_routes.py                   # REST API unit test suite (9 test cases)
├── submission_evidence/                 # Verified submission artifacts & screenshots
│   ├── cicd-github-validate             # Genuine GitHub Actions run record (Run ID 39801269325)
│   ├── oc-pipeline-app-logs             # Genuine pod logs showing SERVICE RUNNING on port 8000
│   ├── pipelinerun.txt                  # Full Tekton pipelinerun execution logs
│   ├── oc-pipelines-console-pvc-details.png  # OpenShift console screenshot: Bound PVC
│   ├── oc-pipelines-oc-final.png        # OpenShift console screenshot: 6-stage cd-pipeline
│   └── oc-pipelines-oc-green.png        # OpenShift console screenshot: Successful cd-pipeline-run-1
├── Dockerfile                           # Container image build manifest (python:3.9-slim)
├── Procfile                             # Process runner definition
├── requirements.txt                     # Application and testing dependencies
├── setup.cfg                            # Test and linter configuration presets
├── pipelinerun.txt                      # Root copy of Tekton PipelineRun logs
├── oc-pipeline-app-logs                 # Root copy of OpenShift pod logs
└── README.md                            # Comprehensive project documentation
```

---

## Continuous Integration (CI) — GitHub Actions

### Workflow Configuration: [`.github/workflows/workflow.yml`](.github/workflows/workflow.yml)

- **Triggers:** Automatically executes on `push` to `main` and `pull_request` targeting `main`.
- **Environment:** Containerized execution inside `python:3.9-slim` on an `ubuntu-latest` GitHub-hosted runner.
- **Workflow Stages:**
  1. **Checkout:** Checks out source code using `actions/checkout@v3`.
  2. **Install dependencies:** Upgrades `pip` and installs requirements from `requirements.txt`.
  3. **Lint with flake8:** Enforces clean code style and catches critical syntax errors (`E9,F63,F7,F82`) as well as complexity limits (`--max-complexity=10 --max-line-length=127`).
  4. **Run unit tests with nose:** Executes unit tests with specifications and code coverage reporting (`nosetests -v --with-spec --spec-color --with-coverage --cover-package=app`).

### CI Verification Results:
- **Workflow Run ID:** `39801269325`
- **Run URL:** [https://github.com/salonitiwari24/ci-cd-final-project/actions/runs/39801269325](https://github.com/salonitiwari24/ci-cd-final-project/actions/runs/39801269325)
- **Job URL:** [https://github.com/salonitiwari24/ci-cd-final-project/actions/runs/39801269325/job/119902290604](https://github.com/salonitiwari24/ci-cd-final-project/actions/runs/39801269325/job/119902290604)
- **Result:** **SUCCESS** (All 9 unit tests passed, 100% code coverage across all service modules, 0 flake8 errors).

---

## Continuous Delivery (CD) — Tekton on Red Hat OpenShift

### Pipeline Architecture: [`tekton/pipeline.yaml`](tekton/pipeline.yaml) / [`.tekton/pipeline.yml`](.tekton/pipeline.yml)

The delivery pipeline consists of 6 sequential tasks running against a shared persistent volume workspace (`pipeline-workspace` bound to `pipelinerun-pvc`):

```
+-----------+     +-------------+     +----------+     +--------+     +-----------+     +----------+
|  cleanup  | --> |  git-clone  | --> |  flake8  | --> |  nose  | --> |  buildah  | --> |  deploy  |
+-----------+     +-------------+     +----------+     +--------+     +-----------+     +----------+
```

1. **`cleanup`**: Runs a root-privileged `alpine:3` container to clean all contents from the shared persistent volume directory without unmounting the storage.
2. **`git-clone`**: Clones the public Git repository (`salonitiwari24/ci-cd-final-project`) at the target branch (`main`) into the workspace.
3. **`flake8`**: Performs static analysis against the `service` package using `python:3.9-slim` with arguments `--count --max-complexity=10 --max-line-length=127 --statistics`.
4. **`nose`**: Sets `DATABASE_URI=$(params.database_uri)`, installs project dependencies, and runs `nosetests $(params.args)` inside `python:3.9-slim`.
5. **`buildah`**: Builds a container image from `Dockerfile` without requiring a Docker daemon and pushes the artifact to the OpenShift Internal Registry (`image-registry.openshift-image-registry.svc:5000/sn-labs-salonitiwari24/hit-counter:latest`).
6. **`deploy`**: Updates `deploy/deployment.yaml` with the newly built image tag using `sed`, applies the manifests with `oc apply -f deploy/`, and verifies pod rollout.

### Persistent Volume Configuration: [`tekton/pvc.yaml`](tekton/pvc.yaml)
- **Name:** `pipelinerun-pvc` (and `oc-lab-pvc`)
- **StorageClass:** `skills-network-learner`
- **AccessModes:** `ReadWriteOnce`
- **Capacity:** `1Gi`
- **Status:** `Bound`

---

## Local and Cloud IDE Execution Guide

### 1. Local Testing & Linting

```bash
# Run Flake8 static analysis
python -m flake8 service --count --select=E9,F63,F7,F82 --show-source --statistics
python -m flake8 service --count --max-complexity=10 --max-line-length=127 --statistics

# Run unit tests
python -m pytest tests/
# Or with nosetests
nosetests -v --with-spec --spec-color --with-coverage --cover-package=service
```

### 2. OpenShift Tekton Execution (IBM Skills Network Cloud IDE)

```bash
# Automated run script
bash bin/run_openshift_pipeline.sh

# Or manual execution:
oc apply -f tekton/pvc.yaml
oc apply -f tekton/tasks.yaml
oc apply -f tekton/pipeline.yaml

tkn pipeline start cd-pipeline \
  -w name=pipeline-workspace,claimName=pipelinerun-pvc \
  -p repo-url="https://github.com/salonitiwari24/ci-cd-final-project.git" \
  -p branch="main" \
  --showlog

# Export pipeline logs
tkn pipelinerun logs -L > pipelinerun.txt

# Verify application deployment & runtime logs
oc rollout status deployment/hit-counter
oc logs deployment/hit-counter
```

### 3. Application Runtime Verification

Application startup logs confirm successful service initialization:
```
[INFO] [log_handlers] Logging handler established
[INFO] [__init__] **********************************************************************
[INFO] [__init__] ********************  S E R V I C E   R U N N I N G  *****************
[INFO] [__init__] **********************************************************************
```

---

## Evidence Artifacts Inventory

| Evidence File | Path | Description | Verification Status |
| :--- | :--- | :--- | :--- |
| **GitHub Actions Run Record** | [`submission_evidence/cicd-github-validate`](submission_evidence/cicd-github-validate) | Verified log of GitHub Actions run #3 (Run ID `39801269325`) | **PASS** |
| **OpenShift Application Logs** | [`submission_evidence/oc-pipeline-app-logs`](submission_evidence/oc-pipeline-app-logs) | Pod runtime logs confirming `SERVICE RUNNING` banner | **PASS** |
| **Full PipelineRun Logs** | [`pipelinerun.txt`](pipelinerun.txt) | Complete stdout of all 6 Tekton pipeline stages | **PASS** |
| **OpenShift PVC Screenshot** | [`submission_evidence/oc-pipelines-console-pvc-details.png`](submission_evidence/oc-pipelines-console-pvc-details.png) | Console screenshot showing `oc-lab-pvc` Bound in `sn-labs-salonitiwari24` | **PASS** |
| **OpenShift Pipeline Screenshot** | [`submission_evidence/oc-pipelines-oc-final.png`](submission_evidence/oc-pipelines-oc-final.png) | Console screenshot showing 6-stage `cd-pipeline` details | **PASS** |
| **OpenShift Green PipelineRun** | [`submission_evidence/oc-pipelines-oc-green.png`](submission_evidence/oc-pipelines-oc-green.png) | Console screenshot showing `cd-pipeline-run-1` Succeeded with all stages green | **PASS** |
| **Kanban Story Screenshot** | `cd-pipeline-done.png` | ZenHub / GitHub Projects Kanban card moved to `Done` | **MANUAL ACTION REQUIRED** |

---

## Course Discrepancy Note

- **Lab Documentation vs Template Repository:** The written lab instructions reference a sample repository `devops-capstone-project`, an `accounts` microservice, and a branch `cd-pipeline`. The official template repository assigned to this project is `ci-cd-final-project` with the `hit-counter` microservice on the `main` branch.
- **Resolution:** This repository implements the complete 6-stage Tekton CD pipeline and GitHub Actions CI workflow using the genuine `hit-counter` microservice codebase, while maintaining full compatibility with the lab parameter structure (`repo-url`, `branch`, `build-image`, `app-name`).

---

## License

Licensed under the Apache License. See [LICENSE](LICENSE).

## Author

IBM Skills Network & Saloni Tiwari (`salonitiwari24`)
