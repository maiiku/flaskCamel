from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail

app = Flask(__name__)

app.config.from_object('flaskcamel.config')
app.secret_key = 'A0Zr$$#@!$44^&fdXHH!'
app.debug = 0

mail = Mail(app)

db = SQLAlchemy(app)

import hooks
import models
import views
