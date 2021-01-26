from api.utils.core import serialize_list, add_new_obj
from api.config import config
from api.utils.FaceEmbedder import get_embeddings
from api.models import Repository, Face, Image, db
from sqlalchemy import and_
import os
import logging
import math
import pickle
import time

logger = logging.getLogger(__name__)

sleep_time = 6
max_checks = 10
batch_size = 8


def embed_faces(repository_id):
    logger.info("initializing embedding")
    repo = Repository.query.filter_by(id=repository_id).first()
    logger.info(f"repo path is: {repo.repository_path}")
    left_to_scan = True
    # keep searching for unembedded faces as long as there are images left to scan in the repo
    counter = 0
    while(left_to_scan):
        logging.info("faces left to scan")
        all_faces = Face.query.join(Image, Image.id == Face.image_id).filter(Image.repository_id == repository_id).filter(Face.embedding == None).all()
        if len(all_faces) > 0:
            logger.info(f"{len(all_faces)} num faces found")
            embedding_ids = [f.id for f in all_faces]
            logger.info(f"getting embeddings for: {embedding_ids}")
            k = 5
            num_iterations = math.ceil(len(all_faces)/k) # will do k faces per batch before sending to db
            # we want to do this because we're only sending embedded faces to user(for guessing)
            for i in range(num_iterations):
                subset_faces = all_faces[(i*k):(i+1)*k]
                facepath_to_obj = {}
                for face in subset_faces:
                    facepath_to_obj[face.face_path] = face
                assert len(facepath_to_obj) == len(subset_faces)
                face_paths = list(facepath_to_obj.keys())
                # logger.debug(f"face paths are: {face_paths}")
                embeddings_ai, face_paths_ai = get_embeddings(repo.repository_path, face_paths, batch_size)
                for i in range(len(face_paths_ai)):
                    path = face_paths_ai[i]
                    embedding = embeddings_ai[i]
                    facepath_to_obj[path].embedding = pickle.dumps(embedding)
                db.session.commit()
            counter = 0
        else:
            if counter == max_checks:
                logger.info("max_checks exceeded. Quitting...")
                break
            else:
                counter += 1
                logger.info(f"no faces found. Will check again in {sleep_time} seconds")
                time.sleep(sleep_time)