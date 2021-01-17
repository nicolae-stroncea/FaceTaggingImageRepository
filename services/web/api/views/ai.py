
from flask import Blueprint, request
from api.models import db, Face, Image, Person, Repository
from api.core import create_response, serialize_list, logger
from webargs import fields
from webargs.flaskparser import use_args

ai = Blueprint("ai", __name__, url_prefix="/api/ai")  # initialize blueprint

@main.route("/face", methods=['POST'])
@use_args({
    "face_path": fields.Str(required=True),
    "image_id": fields.Int(required=True),
    "profile_face": fields.Bool()
})
def post_face(args):
    face = Face(**args)
    add_new_obj(face)
    return create_response(face.to_dict(), 201)