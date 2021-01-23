from typing import List

import logging

logger = logging.getLogger(__name__)

def serialize_list(items: List) -> List:
    """Serializes a list of SQLAlchemy Objects, exposing their attributes.
    
    :param items - List of Objects that inherit from Mixin
    :returns List of dictionaries
    """
    if not items or items is None:
        return []
    return [x.to_dict() for x in items]


def add_new_obj(obj, db):
    if not isinstance(obj, list):
        db.session.add(obj)
        db.session.commit()
        if hasattr(obj, 'id'):
            logger.info(f"{obj.id}")
        logger.info(f"{obj.__tablename__}: {obj.to_dict()}")
    else:
        db.session.add_all(obj)
        db.session.commit()