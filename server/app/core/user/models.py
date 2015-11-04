# -*- coding: utf-8 -*-

from peewee import *
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date
import hashlib
from app.database import db

class User(db.Model):
    __json_hidden__ = ['password_hash']
    
    id = PrimaryKeyField()
    email = CharField(max_length=64, index=True, null=True)
    username = CharField(max_length=64, index=True)
    gender = CharField(max_length=32, default='male')
    location = CharField(max_length=64, null=True)
    job = CharField(max_length=64, null=True)
    education = CharField(max_length=64, null=True)
    slogan = TextField(null=True)
    password_hash = CharField(max_length=128)
    avatar = TextField(null=True)
    confirmed = BooleanField(default=False)
    member_since = DateTimeField(default=datetime.now)
    last_seen = DateTimeField(default=datetime.now)

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.email is not None and self.avatar is None:
            self.avatar = self.get_avatar_url()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def get_avatar_url(self, set='set3', size=100, default='identicon', rating='g'):
        url = 'http://robohash.org'
        hash = self.avatar or hashlib.md5(
            self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}.png?set={set}&size={size1}x{size2}'.format(
            url=url, hash=hash, set=set, size1=size, size2=size)

    def __unicode__(self):
        return '<User %r>' % self.email     