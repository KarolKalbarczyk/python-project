import datetime

import flask
import pdfkit as pdfkit
from flask import redirect, url_for, request, make_response, send_from_directory
import hashlib

import os

from tempfile import NamedTemporaryFile

from InvoiceGenerator.api import Invoice, Item, Client, Provider, Creator

from InvoiceGenerator.pdf import SimpleInvoice
# choose english as language
from injector import inject

from account.account_service import AccountService

os.environ["INVOICE_LANG"] = "en"


from flask_login import login_user, login_required, current_user, logout_user
from wtforms import Form, StringField, PasswordField, validators, ValidationError

from database_definition import db
from account.user import User
from product.entities import Product
from flask_babel import _

from base_render import render_template

import re

class LoginForm(Form):
    email = StringField(_('Email Address'), [validators.DataRequired()])
    password = PasswordField(_('Password'),[validators.DataRequired()])

class RegistrationForm(Form):
    email = StringField(_('Email Address'), [validators.DataRequired()])
    password = PasswordField(_('New Password'), [
        validators.DataRequired(),
        validators.EqualTo(_('confirm'), message=_('Passwords must match'))
    ])
    confirm = PasswordField('Repeat Password')


@login_required
def hello_world():
    return flask.redirect(flask.url_for('products'))

@inject
def login(service: AccountService):
    form = LoginForm(request.form)
    user = User.query.filter_by(email = form.email.data).first()
    if form.validate(extra_validators={ 'password' : [service.good_password(user)]}):
        login_user(user, remember = True)
        next = flask.request.args.get('next')
        return flask.redirect(next or flask.url_for('products'))

    return render_template('login_form.html', form=form)

@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@inject
def sign_up(service: AccountService):
    form = RegistrationForm(request.form)
    if request.method == 'POST':
        if form.validate(extra_validators={'email' : [service.validate_email()] }):
            service.register(form.email.data, form.password.data)
            return redirect(url_for('hello_world'))

    return render_template('sign_up.html', form = form )

