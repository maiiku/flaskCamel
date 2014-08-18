from flask.ext.wtf import Form
from flaskcamel.models import base
from wtforms import StringField, validators, PasswordField, ValidationError


def validate_user(form, username):
    user_by_name = base.Users.query.filter_by(username=username.data).first()
    if user_by_name:
        raise ValidationError('Username already taken. Choose another')


def validate_email(form, email):
    user_by_email = base.Users.query.filter_by(email=email.data).first()
    if user_by_email:
        raise ValidationError(
            "Email already registered. Login or register with another Email"
        )


class DetailForm(Form):
    name = StringField('Payee Name:', [validators.DataRequired()])
    street = StringField('Street Address:', [validators.DataRequired()])
    city = StringField('City/Town:', [validators.DataRequired()])
    phone = StringField('Phone:', [validators.DataRequired()])
    website = StringField('My website:', [validators.DataRequired()])


class SignupForm(Form):
    username = StringField(
        'Username', [
            validators.DataRequired(),
            validate_user,
            validators.Length(min=4, max=25)
        ]
    )
    password = PasswordField(
        'Password', [
            validators.DataRequired(),
            validators.Length(min=4, max=25),
            validators.EqualTo('confirm', message='Passwords must match')
        ]
    )
    confirm = PasswordField('Confirm Password', [validators.DataRequired()])
    email = StringField(
        'eMail', [
            validators.DataRequired(),
            validators.Email(),
            validate_email
        ]
    )


class LoginForm(Form):
    username = StringField('Username', [validators.DataRequired()])
    password = PasswordField('Password', [validators.DataRequired()])


class PasswordResetForm(Form):
    username = StringField('Username')
    email = StringField('eMail')


class ResendConfirmationForm(Form):
    username = StringField('Username')
    email = StringField('eMail')


class PasswordChangeForm(Form):
    password = PasswordField('Password', [validators.DataRequired()])
