import hashlib
from functools import wraps

import flask
from flask import Response, url_for
from flask_httpauth import HTTPBasicAuth
from flask_login import current_user, login_required

from database_definition import db, User

auth = HTTPBasicAuth()


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

def admin_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if current_user.is_anonymous:
            return flask.redirect(url_for('login'))
        user = User.query.filter_by(email = current_user.email).first()
        if user is not None and user.isAdmin:
            return func(*args, **kwargs)
        else:
            return flask.redirect(url_for('login'))
    wrapper.__name__ = func.__name__
    return wrapper


def get_current_user():
    return User.query.filter_by(email = current_user.email).first()