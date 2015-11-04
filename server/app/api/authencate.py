# -*- coding: utf-8 -*-

from flask import request, g
from app.core import userService
from app.exceptions import ServiceError
from . import api, auth
from restful import Restful

# overwrite flask-httpauth error handler
@auth.error_handler
def auth_error():
    # return Restful.bad_request('用户名或密码错误')
    # qq浏览器返回401时，会弹出默认登录登陆框。   在after_request中改变响应头也没用。
    return Restful.forbidden('用户名或密码错误')

@api.before_request
def set_current_user():
    auth = request.authorization
    if not auth:
        g.current_user = None
        return

    email_or_token = auth.username
    password = auth.password

    if password == '':
        g.current_user = userService.verify_auth_token(email_or_token)
    else:
        g.current_user = userService.get_user_by_email(email_or_token)

@api.after_request
def after_request(response):
    # 屏蔽浏览器默认登录窗口
    if response.status_code == 401:
        if response.headers['WWW-Authenticate']:
            response.headers['WWW-Authenticate'] = str(response.headers['WWW-Authenticate']).replace('Basic', 'rdBasic')
    return response

@auth.verify_password
def verify_password(email_or_token, password):
    if password == '':
        user = userService.verify_auth_token(email_or_token)
        g.token_used = True
        return user is not None
    
    user = userService.get_user_by_email(email_or_token)
    if user is None:
        return False
    else:
        g.token_used = False
        return userService.verify_password(user, password)

@api.route('/logout', methods=['POST'])
def logout():
    return Restful.ok()

@api.route('/token')
@auth.login_required
def get_token():
    if g.token_used:
        return Restful.forbidden('请使用用户名和密码')

    return Restful.ok({
            'userId': g.current_user.id,
            'username': g.current_user.username,
            'avatar': g.current_user.avatar,
            'slogan': g.current_user.slogan,
            'token': userService.generate_auth_token(g.current_user.id, 3600*24), 
            'expiration': 3600*24
        })    