from flask import Blueprint
from flask.ext.httpauth import HTTPBasicAuth

api = Blueprint('api', __name__)
auth = HTTPBasicAuth()

from . import error, restful, utils, upload, user, oauth, authencate