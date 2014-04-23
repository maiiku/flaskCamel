from datetime import datetime

from flaskext.bcrypt import Bcrypt
from flask.ext import admin
from flask.ext.login import current_user, UserMixin
from flask.ext.admin.contrib import sqla
from flask.ext.admin.contrib.sqla import filters

from flaskcamel import db, app


ROLE_ADMIN = 0
ROLE_WEB_USER = 1

bcrypt = Bcrypt()


class Users(db.Model, UserMixin):
    __tablename__ = 'users'
    uid = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True)
    pwdhash = db.Column(db.String(60))
    email = db.Column(db.String(60), unique=True)
    fb_id = db.Column(db.String(30), unique=True)
    role = db.Column(db.SmallInteger)
    activate = db.Column(db.Boolean)
    created = db.Column(db.DateTime)

    def __init__(self, username, password, email, role):
        self.username = username
        self.pwdhash = bcrypt.generate_password_hash(password)
        self.email = email
        self.role = role
        self.activate = False
        self.created = datetime.utcnow()

    def check_password(self, password):
        return bcrypt.check_password_hash(self.pwdhash, password)

    def get_role(self):
        return unicode(self.role)

    def is_active(self):
        return self.activate

    def is_authenticated(self):
        return True

    def get_id(self):
        return self.uid

    def __unicode__(self):
        return self.username


# Model for User Details
class userdetail(db.Model):
    __tablename__ = 'userdetail'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False)
    street = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    website = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=True)
    uid = db.Column(db.Integer, db.ForeignKey('users.uid'))
    user = db.relationship('Users',
                           primaryjoin="Users.uid == userdetail.uid",
                           backref=db.backref('users', lazy="joined"))

    def __init__(self, name, street, city, phone, website, date, uid):
        self.name = name
        self.street = street
        self.city = city
        self.phone = phone
        self.website = website
        self.date = date
        self.uid = uid

    def is_verified(self):
        return self.appstatus

    def __unicode__(self):
        return self.website


# Customized User model admin
class UsersAdmin(sqla.ModelView):
    column_sortable_list = ('uid', 'username', 'email', 'created', 'role')
    column_labels = dict(title='Comment Title')
    column_searchable_list = ('username', Users.username)
    column_filters = ('uid',
                      'username',
                      'email',
                      'created',
                      'role',
                      filters.FilterLike(Users.username, 'Fixed Title',
                                         options=(('test1', 'Test 1'),
                                                  ('test2', 'Test 2'))))

    form_args = dict(text=dict(label='Big Text', validators=[]))

    def __init__(self, session):
        super(UsersAdmin, self).__init__(Users, session)

    def is_accessible(self):
        if current_user.get_role() == '0':
            return current_user.is_authenticated()


# Customized UserDetail model admin
class userdetailAdmin(sqla.ModelView):
    column_sortable_list = ('name', 'uid', 'date', 'website')
    column_labels = dict(title='Comment Title')
    column_searchable_list = ('website', userdetail.website)
    column_filters = ('uid',
                      'website',
                      'date',
                      'name',
                      filters.FilterLike(userdetail.website, 'Fixed Title',
                                         options=(('test1', 'Test 1'),
                                                  ('test2', 'Test 2'))))
    form_args = dict(text=dict(label='Big Text', validators=[]))

    def __init__(self, session):
        super(userdetailAdmin, self).__init__(userdetail, session)

    def is_accessible(self):
        if current_user.get_role() == '0':
            return current_user.is_authenticated()

# Create admin
admin = admin.Admin(app, 'FlaskCamel Admin')

# Add views to admin
admin.add_view(UsersAdmin(db.session))
admin.add_view(userdetailAdmin(db.session))
