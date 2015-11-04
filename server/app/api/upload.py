# -*- coding: utf-8 -*-

from flask import current_app, request
from werkzeug import secure_filename
from datetime import datetime
import os, time
from . import api
from restful import Restful

@api.route('/upload/image', methods=['POST'])
def upload_image():
    pass

def _generate_file_name(filename):
    splits = filename.rsplit('.', 1)
    return '%s.%s' % (time.time(), splits[1])

def _is_allowed_file(filename, allowed_set):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_set    




