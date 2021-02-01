import os

import flask
from flask_login import current_user

from account.user import User


def get_supported_languages():
    return os.getenv('langs').split(',')


def render_template(template, *args, **kwargs):
    if current_user.is_anonymous:
        isAdmin = False
    else:
        isAdmin = User.query.filter_by(email = current_user.email).first().isAdmin
    return flask.render_template(template, *args, **kwargs, languages = ['en', 'pl'], isAdmin = isAdmin, url = os.getenv('url'))
