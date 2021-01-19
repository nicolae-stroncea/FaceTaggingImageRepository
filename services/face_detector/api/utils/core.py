from flask import current_app, jsonify
from werkzeug.local import LocalProxy

# logger object for all views to use
logger = LocalProxy(lambda: current_app.logger)