from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
import os
app = Flask(__name__)
env_settings = os.environ.get('FLASKCAMEL_SETTINGS')
if env_settings:
    app.config.from_object(env_settings)
else:
    app.config.from_object('flaskcamel.settings.base')
mail = Mail(app)
db = SQLAlchemy(app)

import models
import hooks
import utils
import views

