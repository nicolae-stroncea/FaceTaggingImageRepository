from flask import Blueprint, request
from api.models import db, Face, Image, Person, Repository
from sqlalchemy import and_
from api.core import create_response, serialize_list, logger
from webargs import fields
from webargs.flaskparser import use_args
from pathlib import Path 
import os
from api.config import config
import requests

main = Blueprint("main", __name__, url_prefix="/api")  # initialize blueprint

def add_new_obj(obj):
    if not isinstance(obj, list):
        db.session.add(obj)
        db.session.commit()
        if hasattr(obj, 'id'):
            logger.info(f"{obj.id}")
        logger.info(f"{obj.__tablename__}: {obj.to_dict()}")
    else:
        db.session.add_all(obj)
        db.session.commit()

def add_directories(repo):
    logger.info("adding directories")
    repo_path = repo.repository_path
    image_paths = []
    extensions = ['.jpg','.JPG']
    for ext in extensions:
        for path in Path(repo_path).rglob(f"*{ext}"):
            formatted_path = Path(str(path).replace(repo_path, ""))
            image_paths.append(str(formatted_path))
    images = []
    for img_path in image_paths:
        images.append(Image(image_path=img_path, repository_id=repo.id))
    add_new_obj(images)
    logger.info(image_paths)

def start_scanning(rep_id):
    logger.info(f"rep_id is: {rep_id}")
    if rep_id == None:
        raise Exception("repositoy id must not be none")
    env = os.environ.get("FLASK_ENV", "dev")
    face_detector_uri = config[env].FACE_DETECTOR_URI
    logger.info(f"request to: {face_detector_uri}")
    data = {
        "repository_id": rep_id
    }
    response = requests.get(f"{face_detector_uri}/start_scan", json=data)
# Repository
@main.route("/repository/<int:id>",methods=['GET'])
def get_repository(id):
    repository = Repository.query.filter_by(id=id).first_or_404()
    return create_response(repository.to_dict())


@main.route("/repository",methods=['POST'])
@use_args({
    "repository_path": fields.Str(required=True),
    "repository_type": fields.Str(missing="local")
})
def post_repository(args):
    rep = Repository(**args)
    add_new_obj(rep)
    add_directories(rep)
    start_scanning(rep.id)
    return create_response(rep.to_dict(), 201)

# Person
@main.route("/person", methods=['POST'])
@use_args({
    "name": fields.Str(required=True)
})
def post_person(args):
    person = Person(**args)
    add_new_obj(person)
    return create_response(person.to_dict(), 201)

# Image
@main.route("/image/person/<int:id>", methods=['POST'])
@use_args({
    "image_path": fields.Str(required=True),
    "repository_id": fields.Int(required=True)
})
def post_image_to_person(args, id):
    img = Image(**args)
    add_new_obj(img)
    #TODO: call to FaceDetector to wake up if not currently woken up, as there's a new image.
    #Think thorugh logic need to be absolutely sure that FaceDetector checks for this.
    # Send person id to the FaceDetector and tell it to add to the face:
    # profile_face=True, person_id_by_human, image_id, face_path
    return create_response(img.to_dict(), 201)

@main.route("/image/<int:id>", methods=['GET'])
def get_image(id):
    image = Image.query.filter_by(id=id).first_or_404()
    return create_response(image.to_dict())
@main.route("/image/person/<int:person_id>", methods=['GET'])
def get_images_for_person(person_id):
    return create_response()
@main.route("/image/repository/<int:repository_id>", methods=['GET'])
def get_images_for_repository(repository_id):
    images = Image.query.filter_by(repository_id=repository_id).all()
    return create_response({"Faces": serialize_list(images)})

#Face
@main.route("/face/<int:id>", methods=['GET'])
def get_face(id):
    face = Face.query.filter_by(id=id).first_or_404()
    return create_response(face.to_dict())

@main.route("/face/known", methods=["GET"])
def get_known_faces():
    # faces = Face.query.join(Person).filter_by(profile_face=True)
    faces = Face.query.filter_by(profile_face=True).all()#.join(Person, Face.person_id_by_human == Person.id)
    serialized_faces = serialize_list(faces)
    # serialized_people = [face.person_by_human.to_dict() for face in faces]
    # logger.info(people_for_faces)
    for i in range(len(serialized_faces)):
        serialized_faces[i]['person_by_human']=faces[i].person_by_human.to_dict()
    logger.info(serialized_faces)
    return create_response({"Faces":serialized_faces})


@main.route("/face/unknown", methods=["GET"])
def get_unknown_faces():
    faces = Face.query.filter(and_(Face.embedding.isnot(None), Face.person_id_by_human == None)).all()
    return create_response({"Faces":serialize_list(faces)})

@main.route("/face/<int:id>/person/<int:person_id>", methods=["PATCH"])
def update_person_for_face(id, person_id):
    face = Face.query.filter_by(id=id).first_or_404()
    face.person_id_by_human = person_id
    db.session.commit()
    logger.info(face.id)
    return create_response(face.to_dict())

@main.route("/face/image/<int:image_id>", methods=["GET"])
def get_faces_for_image(image_id):
    image = Image.query.filter_by(id=image_id).first_or_404()
    faces = image.faces
    logger.info(f"faces: {serialize_list(faces)}")
    return create_response({"faces": serialize_list(faces)})