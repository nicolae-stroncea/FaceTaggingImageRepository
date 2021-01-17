# this file structure follows http://flask.pocoo.org/docs/1.0/patterns/appfactories/
# initializing db in api.models.base instead of in api.__init__.py
# to prevent circular dependencies
from .base import db
from .Repository import Repository
from .Image import Image
from .Face import Face
from .Person import Person


__all__ = ["Repository", "Image", "Face", "Person", "db"]

# You must import all of the new Models you create to this page
