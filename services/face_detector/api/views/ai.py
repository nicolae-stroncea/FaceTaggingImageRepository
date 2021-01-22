
from flask import Blueprint, request, jsonify
from webargs import fields
from webargs.flaskparser import use_args
from api.utils.core import logger, create_response, serialize_list
from api.config import config
from api.utils.FaceDetector import create_faces
from facenet_pytorch import MTCNN
from api.models import Repository, Face, Image, Person, db
from sqlalchemy import and_
from rq import Queue, Connection
import redis
import os
import math

ai = Blueprint("ai", __name__, url_prefix="/")  # initialize blueprint
scanning = False

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

def detect_faces(repository_id):
    logger.info("initializing scanning")
    env = os.getenv("FLASK_ENV", "dev")
    output_dir = config[env].FACE_OUTPUT_DIR
    repo = Repository.query.filter_by(id=repository_id).first()
    # get all images that are not scanned
    all_images = Image.query.filter(and_(Image.repository_id == repository_id,Image.scanned == False)).all()
    num_iterations = math.ceil(len(all_images)/5) # will do 5 images per batch before sending to db
    for i in range(num_iterations):
        images = all_images[(i*5):(i+1)*5]
        considering_ids = [img.id for img in images]
        logger.info(f"considering ids: {considering_ids}")
        imagepath_to_id = {}
        for img in images:
            imagepath_to_id[img.image_path] = img.id
        image_paths = list(imagepath_to_id.keys())
        logger.info(f"repo path is: {repo.repository_path}")
        logger.info(f"image paths are: {image_paths}")
        mtcnn = MTCNN(image_size=160, post_process=False, keep_all=True)
        imagepath_facepath_pairs = create_faces(mtcnn, image_paths, repo.repository_path, output_dir)
        imageid_facepath_pairs = []
        for pair in imagepath_facepath_pairs:
            imageid_facepath_pairs.append((imagepath_to_id[pair[0]],pair[1]))
        logger.info(f"imagepath_facepath_pairs: {imagepath_facepath_pairs}")
        logger.info(f"imageid_facepath_pairs: {imageid_facepath_pairs}")
        faces = []
        for pair in imageid_facepath_pairs:
            faces.append(Face(image_id=pair[0], face_path=pair[1]))
        add_new_obj(faces)
        # set the images to scanned
        logger.info("setting images to scanned")
        for image in images:
            image.scanned = True
        db.session.commit()
        logger.info(f"added: {serialize_list(faces)}")




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
        with Connection(redis.from_url(os.getenv("REDIS_URL"))):
            logger.info("sending task")
            q = Queue()
            task = q.enqueue(detect_faces, repository_id)
    logger.info("sending response")
    return create_response()
