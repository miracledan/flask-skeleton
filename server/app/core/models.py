# -*- coding: utf-8 -*-

from random import seed, randint
import forgery_py
from app.database import db
from user.models import *
from issues.models import *
from tag.models import *
from project.models import *
from activity.models import *
from git.models import *
from blog.models import *

def mock_user(count=10):
    seed()
    items = []
    for i in range(count):
        email = forgery_py.internet.email_address()
        items.append({
            'email': '%d@%d' % (i, i),
            'username': forgery_py.internet.user_name(True),
            'gender': 'female',
            'location': forgery_py.forgery.address.state() + forgery_py.forgery.address.city(),
            'job' : forgery_py.forgery.name.company_name() + forgery_py.forgery.name.job_title(),
            'education' : 'stanford',
            'slogan' : "it's time to show your bigger人",
            'password_hash': generate_password_hash(str(i)),
            'avatar': "http://lorempixel.com/100/100/people?" + str(i),
            'confirmed': True,
            'member_since': forgery_py.date.date(True)
        })

    with db.database.atomic():
        User.insert_many(items).execute()

    return items

def mock_all_models():
    pass