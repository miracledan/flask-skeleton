import os
import logging
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    PROJECT_NAME = 'fs'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SSL_DISABLE = False
    LOG_FILE = '/var/log/%s.log' % PROJECT_NAME
    LOG_MAX_BYTES = 10000
    LOG_BACKUP_COUNT = 1
    LOG_FORMATTER = logging.Formatter("[%(asctime)s] {%(pathname)s:%(lineno)d} " \
        "%(levelname)s - %(message)s")
    LOG_LEVEL = logging.DEBUG
    
    @staticmethod
    def init_app(cls, app):
        # config log
        from logging.handlers import RotatingFileHandler
        handler = RotatingFileHandler(cls.LOG_FILE, maxBytes=cls.LOG_MAX_BYTES, 
            backupCount=cls.LOG_BACKUP_COUNT)
        handler.setLevel(cls.LOG_LEVEL)
        handler.setFormatter(cls.LOG_FORMATTER)
        app.logger.addHandler(handler)

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE = {
        'name': os.environ.get('DEV_DB_NAME') or Config.PROJECT_NAME,
        'engine': 'playhouse.pool.PooledMySQLDatabase',
        # 'engine': 'peewee.MySQLDatabase',
        'host': '192.168.2.100',
        'port': 3306,
        'user': 'root', 
        'passwd': "admin123",
        'max_connections': 20,
        'stale_timeout': 300,
        'charset':'utf8mb4',
        # using peewee and gevent, belowing must be set.
        'threadlocals':True
    }

    @classmethod
    def init_app(cls, app):
        Config.init_app(cls, app)

class ProductConfig(Config):
    DATABASE = {
        'name': os.environ.get('DEV_DB_NAME') or Config.PROJECT_NAME,
        'engine': 'playhouse.pool.PooledMySQLDatabase',
        'host': 'localhost',
        'port': 3306,
        'user': 'root', 
        'passwd': "admin123",
        'max_connections': 100,
        'stale_timeout': 300,
        'charset':'utf8mb4',
        # using peewee and gevent, belowing must be set.
        'threadlocals':True
    }

    @classmethod
    def init_app(cls, app):
        Config.init_app(cls, app)

class SqliteConfig(Config):
    DEBUG = True
    DATABASE = {
        'name': '%s-dev.db' % Config.PROJECT_NAME,
        'engine': 'peewee.SqliteDatabase',
        'check_same_thread': False,
    }

class TestingConfig(Config):
    TESTING = True
    DATABASE = {
        'name': '%s-test.db' % Config.PROJECT_NAME,
        'engine': 'peewee.SqliteDatabase',
        'check_same_thread': False,
    }
    WTF_CSRF_ENABLED = False   
    LOG_FILE = 'log/test.log' 

    @classmethod
    def init_app(cls, app):
        Config.init_app(cls, app)

config = {
    'default': DevelopmentConfig,
    'testing': TestingConfig,
    'product': ProductConfig
}
