from base import *
DEBUG = 1

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(
    basedir, '../my_dev_db.db'
)
#config for mailcatcher
MAIL_USERNAME = None
MAIL_PASSWORD = None
MAIL_USE_SSL = False
MAIL_SERVER = 'localhost'
MAIL_PORT = 1025
MAIL_DEBUG = 0