from flask_mail import Mail, Message
from __init__ import app

from itsdangerous import URLSafeTimedSerializer

app.config.update(dict(
    DEBUG = True,
    MAIL_SERVER = 'smtp.gmail.com',
    MAIL_PORT = 587,
    MAIL_USE_TLS = True,
    MAIL_USE_SSL = False,
    MAIL_USERNAME = 'karol.kalbarczyk.radom@gmail.com',
    MAIL_PASSWORD = '12OFFde#ff4388',
))
mail = Mail(app)


class EmailService():

    def send_confirmation_email(self, email):
        ts = URLSafeTimedSerializer(app.config["SECRET_KEY"])
        msg = Message('Hello', sender='karol.kalarczyk.radom@gmail.com', recipients=[email])
        msg.body = "placeholder"
        mail.send(msg)

    def send_email(self, email, message):
        try:
            msg = Message('Hello', sender='karol.kalarczyk.radom@gmail.com', recipients=[email])
            msg.body = message
            mail.send(msg)
        except:
            app.logger.info("Couldn't send mail")
