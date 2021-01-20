
from flask import Blueprint, request, jsonify
# from api.core import create_response, serialize_list, logger
from webargs import fields
from webargs.flaskparser import use_args
from api.utils.core import logger
from api.utils.core import create_response
from api.config import config
from api.utils.FaceDetector import create_faces
from facenet_pytorch import MTCNN
import os

ai = Blueprint("ai", __name__, url_prefix="/")  # initialize blueprint
scanning = False





@ai.route("/", methods=['GET'])
def get():
    logger.info("getting resources")
    return jsonify({"test":"hello world"}), 200

@ai.route("/start_scan", methods=['GET'])
@use_args({
    "repository_id": fields.Int(required=True),
})
def start_scan(args):
    repository_id = args["repository_id"]
    logger.info(f"rep_id is: {repository_id}")
    global scanning
    env = os.environ.get("FLASK_ENV", "dev")
    if not scanning:
        scanning = True
        logger.info("initializing scanning")
        output_dir = config[env].FACE_OUTPUT_DIR
        # create_faces(image_paths, repo_path, output_dir)
    return create_response()
