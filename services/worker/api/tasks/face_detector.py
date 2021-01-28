
from api.utils.core import serialize_list, add_new_obj
from api.config import config
from api.utils.FaceDetector import create_faces
from facenet_pytorch import MTCNN
from api.models import Repository, Face, Image, db
from sqlalchemy import and_
import os
import math
import logging

logger = logging.getLogger(__name__)


def detect_faces(repository_id):
    logger.info("initializing scanning")
    env = os.getenv("FLASK_ENV", "dev")
    output_dir = config[env].FACE_OUTPUT_DIR
    repo = Repository.query.filter_by(id=repository_id).first()
    # get all images that are not scanned
    all_images = Image.query.filter(and_(Image.repository_id == repository_id,Image.scanned == False)).all()
    num_iterations = math.ceil(len(all_images)/5) # will do 5 images per batch before sending to db
    logging.info(f"number of iterations is: {num_iterations}")
    for i in range(num_iterations):
        logger.info("new iteration")
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
        add_new_obj(faces, db)
        # set the images to scanned
        logger.info("setting images to scanned")
        for image in images:
            image.scanned = True
        db.session.commit()
        logger.info(f"added: {serialize_list(faces)}")
    logging.info("finished detecting faces")
