
import os
import logging
from flask import Flask, request
from flask_cors import CORS
from api.config import config
from api.utils.core import all_exception_handler



# why we use application factories http://flask.pocoo.org/docs/1.0/patterns/appfactories/#app-factories
def create_app(test_config=None):
    """
    The flask application factory. To run the app somewhere else you can:
    ```
    from api import create_app
    app = create_app()

    if __main__ == "__name__":
        app.run()
    """
    app = Flask(__name__)

    CORS(app)  # add CORS

    env = os.environ.get("FLASK_ENV", "dev")
    app.config.from_object(config[env])
    formatter = logging.Formatter("%(asctime)s: %(levelname)s in [%(module)s: %(lineno)d]: %(message)s")
    if app.config.get("LOG_FILE"):
        fh = logging.FileHandler(app.config.get("LOG_FILE"))
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        app.logger.addHandler(fh)

    strm = logging.StreamHandler()
    strm.setLevel(logging.DEBUG)
    strm.setFormatter(formatter)
    app.logger.addHandler(strm)
    app.logger.setLevel(logging.DEBUG)

    # root = logging.getLogger("core")
    # root.addHandler(strm)

    # register sqlalchemy to this app
    from api.models import db
    db.init_app(app)  # initialize Flask SQLALchemy with this flask app


    # import and register blueprints
    from api.views import ai
    app.register_blueprint(ai.ai)
    # register error Handler
    app.register_error_handler(Exception, all_exception_handler)

    return app
