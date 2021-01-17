
from flask import Blueprint, request
from api.models import db, Face, Image, Person, Repository
from api.core import create_response, serialize_list, logger
from webargs import fields
from webargs.flaskparser import use_args
import pickle
import numpy as np

dev = Blueprint("dev", __name__, url_prefix="/api/dev")  # initialize blueprint


@dev.route("/db",methods=['GET'])
def fill_tables():
    r1 = Repository(repository_path="img_dir", repository_type="local")
    p1 = Person(name="Nick")
    p2 = Person(name="John")
    p3 = Person(name="Mary")
    img1 = Image(image_path = "img1.png", repository=r1)
    img2 = Image(image_path = "img2.png", repository=r1)
    face1 = Face(face_path=".face/f1.png",
        image=img1, person_by_human=p1, profile_face=True)
    face2 = Face(face_path=".face/f2.png",
        image=img1, person_by_human=p2, profile_face=True)
    # want to check getting unknown faces
    np_arr = np.array([1,2,4,3],dtype=np.float32)
    bin_data = pickle.dumps(np_arr)
    logger.info(bin_data)
    face3 = Face(face_path=".face/f3.png",
        image=img2, embedding=bin_data)
    db.session.add_all([face1,face2,face3])
    db.session.commit()
    return create_response()

@dev.route("/db",methods=['DELETE'])
def drop_all():
    db.drop_all()
    db.create_all()
    db.session.commit()
    return create_response()