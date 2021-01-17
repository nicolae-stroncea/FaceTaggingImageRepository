from api.core import Mixin
from .base import db

# Note that we use sqlite for our tests, so you can't use Postgres Arrays
class Image(Mixin, db.Model):
    """Image Table."""

    __tablename__ = "image"
    id = db.Column(db.Integer, primary_key=True)
    image_path = db.Column(db.String(1024), nullable=False)
    scanned = db.Column(db.Boolean, default=False)
    repository_id = db.Column(db.Integer, db.ForeignKey('repository.id'), nullable=False)
    
    faces = db.relationship('Face', backref="image")
    # repository = db.relationship("Repository", back_populates="images")


    def __repr__(self):
        return f"<Image {self.image_path}>"
