from flask import request, session, Response
from flask_babel import Babel
import os
from main import app
from base_render import get_supported_languages
langKey = 'lang'

babel = Babel(app)

@babel.localeselector
def get_locale():
    supportedLangs = get_supported_languages()
    lang = session.get(langKey)
    if lang is not None:
        return lang
    return request.accept_languages.best_match(supportedLangs)

def set_lang():
    supportedLangs = get_supported_languages()
    lang = request.args.get('lang')
    if lang not in supportedLangs:
        return Response('', status=200)
    else:
        session[langKey] = lang
        return Response('', status=200)

