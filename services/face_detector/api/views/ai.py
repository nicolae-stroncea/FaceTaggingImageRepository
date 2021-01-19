
from flask import Blueprint, request, jsonify
# from api.core import create_response, serialize_list, logger
from webargs import fields
from webargs.flaskparser import use_args
from api.utils.core import logger
ai = Blueprint("ai", __name__, url_prefix="/")  # initialize blueprint





@ai.route("/", methods=['GET'])
def get():
    logger.info("getting resources")
    return jsonify({"test":"hello world"}), 200

