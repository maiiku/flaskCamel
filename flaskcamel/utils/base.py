from flask import render_template, g
from flask.ext.login import AnonymousUserMixin, LoginManager, current_user
from flask.ext.mail import Mail
from flaskcamel.decorators import async
from flaskcamel import app, db
from flaskcamel.models.base import Users

mail = Mail(app)

class Anonymous(AnonymousUserMixin):
    name = u"Anonymous"

login_manager = LoginManager()
login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"
login_manager.init_app(app)

@async
def send_async_email(msg):
    with app.app_context():
        mail.send(msg)


@app.errorhandler(404)
def internal_error404(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error500(error):
    db.session.rollback()
    return render_template('500.html'), 500

@login_manager.user_loader
def load_user(uid):
    return Users.query.filter_by(uid=uid).first()

@app.before_request
def before_request():
    g.user = current_user
