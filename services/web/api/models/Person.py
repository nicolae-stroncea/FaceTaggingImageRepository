from api.core import Mixin
from .base import db


class Person(Mixin, db.Model):
    """Person Table."""

    __tablename__ = "person"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    embedding = db.Column(db.LargeBinary)

    # faces_by_human = db.relationship('Face', backref="person_by_human")
    # faces_by_ai = db.relationship('Face', backref="person_by_ai")


    def __repr__(self):
        return f"<Person {self.name}>"
