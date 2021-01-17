from api.core import Mixin
from .base import db


class Face(Mixin, db.Model):
    """Face Table."""

    __tablename__ = "face"

    id = db.Column(db.Integer, primary_key=True)
    face_path = db.Column(db.String(1024), unique=True, nullable=False)
    image_id = db.Column(db.Integer, db.ForeignKey('image.id'), nullable=False)
    # True if this is a face to show to the user for person_id
    profile_face = db.Column(db.Boolean, default=False)
    embedding = db.Column(db.LargeBinary)
    person_id_by_human = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=True)
    person_id_by_ai    = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=True)
    
    person_by_human = db.relationship("Person", backref="faces_by_human", foreign_keys=[person_id_by_human])
    person_by_ai = db.relationship("Person", backref="faces_by_ai", foreign_keys=[person_id_by_ai])
    # image = db.relationship("Image", back_populates="faces")


    def __repr__(self):
        return f"<face {self.face_path}>"
