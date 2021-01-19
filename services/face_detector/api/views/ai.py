
from flask import Blueprint, request, jsonify
# from api.core import create_response, serialize_list, logger
from webargs import fields
from webargs.flaskparser import use_args
from api.utils.core import logger
# from api.utils.FaceDetector import 
ai = Blueprint("ai", __name__, url_prefix="/")  # initialize blueprint
scanning = False
# from facenet_pytorch import MTCNN




@ai.route("/", methods=['GET'])
def get():
    logger.info("getting resources")
    return jsonify({"test":"hello world"}), 200

@ai.route("/start_scan", methods=['GET'])
def start_scan():
    global scanning
    if not scanning:
        scanning = True
        logger.info("initializing scanning")
    return jsonify({"test":"hello world"}), 200
