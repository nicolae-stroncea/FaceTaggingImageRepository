from flask import Blueprint, send_from_directory
from api.config import config
import os

static_blueprint = Blueprint("static", __name__, url_prefix="/")  # initialize blueprint

#static routes
@static_blueprint.route("/static/<path:filename>")
def staticfiles(filename):
    env = os.environ.get("FLASK_ENV", "dev")
    folder_dir = config[env].STATIC_FOLDER
    return send_from_directory(folder_dir, filename)


@static_blueprint.route("/media/<path:filename>")
def mediafiles(filename):
    env = os.environ.get("FLASK_ENV", "dev")
    folder_dir = config[env].MEDIA_FOLDER
    return send_from_directory(folder_dir, filename)