# -*- coding: utf-8 -*-

import operator
from flask import current_app, g
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from peewee import DoesNotExist, fn, JOIN
from app.database import db
from app.utils import singleton
from app.exceptions import ServiceError, PeeweeError
from ..activity.service import activityService
from ..models import User

@singleton
class UserService(object):
    
    @db.database.atomic()
    def register(self, data):
        if 'id' in data:
            del data ['id']
        user = User(**data)
        user.confirm=True

        if user.oauth_id is None and self.check_email_used(user.email):
            raise ServiceError('邮箱: %s 已经被使用' % user.email)

        user.save()
        return user

    @db.database.atomic()
    def modify_user_profile(self, uid, data):
        if g.current_user.id != int(uid):
            raise ServiceError('非用户本人不可修改')
        
        user = self.get_user_by_id(uid)
        if user == None:
            raise ServiceError('用户ID: %s 不存在' % uid)

        #改密码
        if 'newPassword' in data:
            if not self.verify_password(user, data['oldPassword']):
                raise ServiceError('旧密码验证失败')
            else:
                user.password = data['newPassword']

        try:
            user.update_model(data, ['id', 'email', 'password', 'password_hash'])
        except PeeweeError:
            pass

        user.save()
        self.spider_user_sns(user)
        return user

    def generate_auth_token(self, uid, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': uid}).decode('ascii')

    def verify_password(self, user, password):
        return check_password_hash(user.password_hash, password)

    def verify_auth_token(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            return User.get(User.id==data['id'])
        except:
            return None

    def ping(self, user):
        '''refresh user last_seen'''
        user.last_seen = datetime.now()
        user.save()   

    def check_email_used(self, email):
        return User.select().where(User.email == email).exists()
    
    def get_user_list(self, **kwargs):
        '''
        kwargs:{
            fuzzy : str,
        }
        '''
        where = []
        if kwargs.get('fuzzy', '') != '':
            where.append(fn.concat_ws(",", User.username, User.email) % kwargs.get('fuzzy').join(('%', '%')))
        
        return User.select().where(reduce(operator.and_, where) if len(where) != 0 else None).naive()    

    def get_user_by_id(self, uid):
        try:
            return User.get(User.id == uid)
        except DoesNotExist:
            return None

    def get_user_by_email(self, email):
        if (email is None or email == ''):
            return None

        try:
            return User.get(User.email == email)
        except DoesNotExist:
            return None

userService = UserService()        
