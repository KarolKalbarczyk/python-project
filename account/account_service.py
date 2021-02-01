import datetime
import hashlib
import re
from flask_babel import _
from wtforms import ValidationError

from database_definition import User, db


class AccountService():

    def register(self, email, password):
        user = User(email=email,
                    password=self.__hash_password(password),
                    joinDate=datetime.date.today(),
                    isActive=True)

        db.session.add(user)
        db.session.commit()

    def __hash_password(self, password):
        return hashlib.md5(password.encode()).hexdigest()

    def validate_email(self):
        def _validate(form, field):
            email = field.data
            if not re.match("[a-zA-Z0-9.!?]{1,64}@[a-zA-Z0-9!?]*\.[a-zA-Z]{0,4}", email):
                raise ValidationError(_('Not a valid e-mail'))

            users = User.query.filter_by(email=email).all()
            if len(users) > 0:
                raise ValidationError(_('This email address is already taken.'))

        return _validate


    def good_password(self, user):
        message = _('Wrong email or password')

        def _length(form, field):
            password = field.data
            if user is None or user.password != self.__hash_password(password):
                raise ValidationError(message)

        return _length
