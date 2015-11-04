# -*- coding: utf-8 -*-

from flask import request, g, url_for
from app.core import userService, projectService, issuesService
from app.exceptions import ServiceError
from . import api, auth
from restful import Restful
from utils import Paginate, safe_model_to_json, get_request_page_args

def enrich_user(user):
    user.followees          = userService.count_user_followees(user.id)
    user.followers          = userService.count_user_followers(user.id)
    user.followdByMe        = userService.check_user_followed_by_me(user.id)
    user.followsMe          = userService.check_user_following_me(user.id)
    user.starredIssues      = {
        'count': issuesService.count_user_starred_issues(user.id),
        'list': [item.to_json() for item in issuesService.get_starred_issues_list(user.id, 1, 7)]
    }
    user.starredProject     = {
        'count': projectService.count_user_starred_project(user.id), 
        'list': [item.to_json() for item in projectService.get_starred_project_list(user.id, 1, 7)]
    }
    user.contributedProject = {
        'count': projectService.count_user_contributed_project(user.id), 
        'list': [item.to_json() for item in projectService.get_contributed_project_list(user.id, 1, 7)]
    }
    user.joinedProject      = {
        'count': projectService.count_user_joined_project(user.id), 
        'list': [item.to_json() for item in projectService.get_joined_project_list(user.id, 1, 7)]
    }
    user.snsInfo = userService.get_user_sns_info(user.id)

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

@api.route('/user/<id>/ability')
def get_user_ability_analysis(id):
    paginate = Paginate(userService.get_vote_by_id(id), url_for('api.get_user_ability_analysis', id=id), 1, 10)
    return Restful.ok(paginate.to_json())
