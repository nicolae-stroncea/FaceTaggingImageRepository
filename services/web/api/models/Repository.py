from api.core import Mixin
from .base import db

# Note that we use sqlite for our tests, so you can't use Postgres Arrays
class Repository(Mixin, db.Model):
    """Repository Table."""

    __tablename__ = "repository"
    id = db.Column(db.Integer, primary_key=True)
    repository_path = db.Column(db.String(1024), unique=True, nullable=False)
    # last_checked = db.Column(db.DateTime, nullable=False)
    repository_type = db.Column(db.String(40),nullable=False)

    images = db.relationship('Image', backref="repository")

    def __repr__(self):
        return f"<Repository {self.repository_path}>"
