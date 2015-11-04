# -*- coding: utf-8 -*-

import json
from flask import request, g, url_for, render_template, current_app
from app.core import oauthService, userService
from app.exceptions import ServiceError
from . import api, auth
from restful import Restful

@api.route('/oauth/<server_name>')
def oauth_login(server_name):
    server = oauthService.getServer(server_name)
    if server is None:
        return render_template('oauth.html', success=False, data='暂不支持该第三方登录接口:%s' % server_name)

    rest = server.remote_app.authorize(callback=url_for('api.oauth_authorized', server_name=server_name, _external=True))
    return rest

@api.route('/oauth/<server_name>/callback')
def oauth_authorized(server_name):
    server = oauthService.getServer(server_name)
    if server is None:
        return render_template('oauth.html', success=False, data='暂不支持该第三方登录接口:%s' % server_name)

    resp = server.remote_app.authorized_response()
    if resp is None:
        return render_template('oauth.html', success=False, data='Access denied: reason=%s error=%s' % 
            (request.args['error'], request.args['error_description']))

    server.save_info(resp)
    user = server.get_user()

    if user is None:
        return render_template('oauth.html', success=False, data='获取用户信息失败,无法登录.')

    exist = userService.get_user_by_oauth_id(user['oauth_id'])
    if exist is None:
        try:
            exist = userService.register(user)
        except ServiceError, e:
            return render_template('oauth.html', success=False, data=e.message)
    
    g.current_user = exist
    token = {
        'userId': g.current_user.id,
        'username': g.current_user.username,
        'avatar': g.current_user.avatar,
        'slogan': g.current_user.slogan,
        'token': userService.generate_auth_token(g.current_user.id, 3600*24), 
        'expiration': 3600*24
    }

    return render_template('oauth.html', success=True, data=token)
