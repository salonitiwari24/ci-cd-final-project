"""
Service Package
"""
import sys
from flask import Flask
from flask_talisman import Talisman
from flask_cors import CORS
from service.common import log_handlers

app = Flask(__name__)

# Initialize Talisman security headers
talisman = Talisman(app)

# Initialize CORS
cors = CORS(app)

# This must be imported after the Flask app is created
from service import routes  # noqa: F401 E402 # pylint: disable=wrong-import-position,cyclic-import

log_handlers.init_logging(app, "gunicorn.error")

app.logger.info(70 * "*")
app.logger.info("  S E R V I C E   R U N N I N G  ".center(70, "*"))
app.logger.info(70 * "*")
