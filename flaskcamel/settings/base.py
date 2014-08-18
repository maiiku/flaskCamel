import os

DEBUG = 0
CSRF_ENABLED = True
SECRET_KEY = '4740e2b#$%$dsfds55wer#455'

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
    basedir, '../my_database.db'
)
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, '../db_repository')
STATIC_ROOT = None

#EMAIL SETTINGS
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'your_gmail_id@gmail.com'
MAIL_PASSWORD = 'your_gmail_pass'
MAIL_DEBUG = 0

APPLICATION_LONG_NAME = 'flaskCamel - blue box for flask applications'
APPLICATION_SHORT_NAME = 'flaskCamel'