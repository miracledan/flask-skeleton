import math
from flask import url_for
from peewee import SelectQuery
from functools import wraps
from playhouse.shortcuts import *

class Paginate(object):
    '''
    paginate_by: data count per page
    offset: curr page number
    prev: url for prev page
    next: url for next page
    total: total data count
    '''
    def __init__(self, query_or_model, url, page, paginate_by):
        self.paginate_by = paginate_by
        self.page = page
        self.url = url

        if isinstance(query_or_model, SelectQuery):
            self.query = query_or_model
            self.model = self.query.model_class
        else:
            self.model = query_or_model
            self.query = self.model.select()

        self.data = self.query.paginate(self.page, self.paginate_by)
        self.total = self.query.count()
        #self.page = int(math.ceil(float(self.total) / self.limit))
        self.prev = page > 1 and page-1 or None
        self.next = page < int(math.ceil(float(self.total) / self.paginate_by)) and page+1 or None

    def to_json(self):
        return {
            'data': [item.to_json() for item in self.data],
            'prev': self.url + '/?page=' + str(self.prev) + '&paginate_by=' + str(self.paginate_by),
            'next': self.url + '/?page=' + str(self.next) + '&paginate_by=' + str(self.paginate_by),
            'page': self.page,
            'paginate_by': self.paginate_by,
            'total': self.total
        }

# item.to_json()
def jsonify_list():
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return [item.to_json for item in f(*args, **kwargs)]
        return wrapper
    return decorator

def safe_model_to_json(model):
    return model and model.to_json()

def get_request_page_args(requset, page_default=1, paginate_default=20):
    page = requset.args.get('page', page_default, type=int)
    paginate_by = requset.args.get('paginate_by', paginate_default, type=int)
    return page, paginate_by