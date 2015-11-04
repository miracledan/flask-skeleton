# -*- coding: utf-8 -*-

from flask import request, g, url_for
from app.core import userService
from app.exceptions import ServiceError
from . import api, auth
from restful import Restful
from utils import Paginate, safe_model_to_json, get_request_page_args

def enrich_user(user):
    return user

@api.route('/user')
def get_user_list():
    fuzzy = request.args.get('fuzzy', type=str)
    order = request.args.get('order', type=str)
    page, paginate_by = get_request_page_args(request)
    paginate = Paginate(userService.get_user_list(fuzzy=fuzzy), '/user', page, paginate_by)

    return Restful.ok(paginate.to_json())    


@api.route('/user/<id>')
def get_user(id):
    user = userService.get_user_by_id(id)
    if user is None:
        return Restful.bad_request('用户ID: %s 不存在' % id)

    user = safe_model_to_json(enrich_user(user))
    return Restful.ok(user)

@api.route('/user', methods=['POST'])
def register():
    try:
        user = userService.register(request.json)
        return Restful.created({
                'userId': user.id,
                'username': user.username,
                'avatar': user.avatar,
                'slogan': user.slogan,
                'token': userService.generate_auth_token(user.id, 3600*24),
                'expiration': 3600*24
            })
    except ServiceError, e:
        return Restful.bad_request(e.message)

@api.route('/user/<id>', methods=['PATCH'])
@auth.login_required
def modify_user(id):
    try:
        user = userService.modify_user_profile(id, request.json)
        return Restful.ok(user.to_json())
    except ServiceError, e:
        return Restful.bad_request(e.message)

@api.route('/user/<id>/sns', methods=['PATCH'])
@auth.login_required
def update_user_sns(id):
    user = userService.get_user_by_id(id)
    if user is None:
        return Restful.bad_request('用户ID: %s 不存在' % id)

    userService.spider_user_sns(user)
    return Restful.ok()
