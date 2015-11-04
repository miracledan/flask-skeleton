from flask import current_app, request, render_template
from app.exceptions import ValidationError
from . import api
from restful import Restful

# overwrite flask app error handler
@api.app_errorhandler(404)
def app_page_not_found(e):
    current_app.logger.error(e)
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = Restful.page_not_found()
        return response
    return render_template('404.html'), 404

@api.app_errorhandler(405)
def app_method_not_allowed(e):
    current_app.logger.error(e)
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = Restful.method_not_allowed()
        return response
    return render_template('405.html'), 405

@api.app_errorhandler(500)
def app_internal_server_error(e):
    current_app.logger.error(e)
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = Restful.internal_server_error(e.message)
        return response
    return render_template('500.html'), 500


# process exception 'ValidationError'
@api.errorhandler(ValidationError)
def validation_error(e):
    current_app.logger.error(e)
    return Restful.bad_request(e.message) 

# @api.errorhandler(Exception)
# def validation_error(e):
#     current_app.logger.error(e)
#     return Restful.internal_server_error(e)