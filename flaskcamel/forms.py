from flask.ext.wtf import Form
from wtforms import TextField, validators, PasswordField, ValidationError

import models


def validate_user(form, username):
    user_by_name = models.Users.query.filter_by(username=username.data).first()
    if user_by_name:
        raise ValidationError('Username already taken. Choose another')


def validate_email(form, email):
    user_by_email = models.Users.query.filter_by(email=email.data).first()
    if user_by_email:
        raise ValidationError("Email already registered. Login or register \
                               with another Email")


class DetailForm(Form):
    name = TextField('Payee Name:', [validators.Required()])
    street = TextField('Street Address:', [validators.Required()])
    city = TextField('City/Town:', [validators.Required()])
    phone = TextField('Phone:', [validators.Required()])
    website = TextField('My website:', [validators.Required()])


class SignupForm(Form):
    username = TextField('Username', [validators.Required(),
                         validate_user, validators.Length(min=4, max=25)])
    password = PasswordField('Password', [validators.Required(),
                             validators.Length(min=4, max=25),
                             validators.EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Confirm Password', [validators.Required()])
    email = TextField('eMail', [validators.Required(),
                      validators.Email(), validate_email])


class LoginForm(Form):
    username = TextField('Username', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])


class PasswordResetForm(Form):
    username = TextField('Username')
    email = TextField('eMail')


class PasswordChangeForm(Form):
    password = PasswordField('Password', [validators.Required()])
