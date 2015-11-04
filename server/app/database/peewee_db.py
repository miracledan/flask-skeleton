# -*- coding: utf-8 -*-

import sys, json, peewee, re
from playhouse.migrate import MySQLMigrator
from app.exceptions import PeeweeError
from app.serializer import PeeweeJsonSerializer


class Database(object):
    database_proxy = peewee.Proxy()

    def __init__(self):
        self.Model = self.get_model_class()

    def init_app(self, app, database=None):
        self.app = app
        self.database = database

        if self.database is None:
            self.load_database()

        self.register_handlers()
        
        self.database_proxy.initialize(self.database)

        self.migrator = MySQLMigrator(self.database)


    def load_database(self):
        self.database_config = dict(self.app.config['DATABASE'])
        try:
            self.database_name = self.database_config.pop('name')
            self.database_engine = self.database_config.pop('engine')
        except KeyError:
            raise PeeweeError('Please specify a "name" and "engine" for your database')

        try:
            self.database_class = self.load_class(self.database_engine)
            assert issubclass(self.database_class, peewee.Database)
        except ImportError:
            raise PeeweeError('Unable to import: "%s"' % self.database_engine)
        except AttributeError:
            raise PeeweeError('Database engine not found: "%s"' % self.database_engine)
        except AssertionError:
            raise PeeweeError('Database engine not a subclass of peewee.Database: "%s"' % self.database_engine)

        self.database = self.database_class(self.database_name, **self.database_config)

    def get_model_class(self):
        class BaseModel(peewee.Model, PeeweeJsonSerializer):               
            class Meta:
                database = self.database_proxy
                
                # define table name
                def db_table_func(cls):
                    return re.sub('([a-z])([A-Z])', '\g<1>_\g<2>', cls.__name__).lower()

            def update_model(self, new_info, except_fields=['id']):
                invalid_info = {}
                for key in new_info:
                    if (key in self._data.keys()) and (key not in except_fields):
                        self._data[key] = new_info[key]
                    elif hasattr(self, key):
                        setattr(self, key, new_info[key])
                    else:
                        invalid_info[key] = new_info[key]

                if len(invalid_info) != 0:
                    raise PeeweeError('以下字段不存在: %s' % json.dumps(invalid_info))

        return BaseModel


    def connect_db(self):
        self.database.connect()

    def close_db(self, exc):
        if not self.database.is_closed():
            self.database.close()

    def register_handlers(self):
        self.app.before_request(self.connect_db)
        self.app.teardown_request(self.close_db)

    def load_class(self, s):
        path, klass = s.rsplit('.', 1)
        __import__(path)
        mod = sys.modules[path]
        return getattr(mod, klass)

    def create_tables(self, models):
        self.database.create_tables(models, safe=True)

    def drop_tables(self, models):
        self.database.drop_tables(models, safe=True)

db = Database()
