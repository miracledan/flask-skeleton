# set python env utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from flask import Flask
from flask.ext.cors import CORS
from flask.ext.compress import Compress
from flask.ext.assets import Bundle, Environment
from config import config
from database import db

compress = Compress()
assets = Environment()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # use gzip compress response
    compress.init_app(app)

    # init database
    db.init_app(app)

    # init static resource
    # assets.init_app(app)
    # bundles = {
    #     'fullpage_css': Bundle(
    #         'css/base.css',
    #         output='gen/base.css',
    #         filters='cssmin'),

    #     'fullpage_js': Bundle(
    #         'js/base.js',
    #         output='gen/base.js',
    #         filters='jsmin'),
    # }
    # assets.register(bundles)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    #solve the CORS problem(cross domain request)
    CORS(app, resources={r'/api/*': {"origins": "*"}})

    return app    



   