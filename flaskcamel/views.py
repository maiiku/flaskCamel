from datetime import datetime, date

from itsdangerous import URLSafeSerializer

from flask import render_template, url_for, redirect, flash, request, session
from flask.ext.login import (LoginManager, current_user, login_required,
                             login_user, logout_user, AnonymousUser)
from flask.ext.mail import Mail, Message
from flaskext.bcrypt import Bcrypt
from flask_debugtoolbar import DebugToolbarExtension
from flask.ext.oauth import OAuth

from forms import SignupForm, LoginForm, PasswordResetForm, PasswordChangeForm, DetailForm
from flaskcamel import app, db
from models import Users, UserDetail
from decorators import async

oauth = OAuth()
toolbar = DebugToolbarExtension(app)
bcrypt = Bcrypt()
mail = Mail(app)

# Faceboook App Credentials
facebook = oauth.remote_app('facebook',
                            base_url='https://graph.facebook.com/',
                            request_token_url=None,
                            access_token_url='/oauth/access_token',
                            authorize_url='https://www.facebook.com/dialog/oauth',
                            consumer_key='your_consumer_key',
                            consumer_secret='your_secret_key',
                            request_token_params={'scope': 'email'})


class Anonymous(AnonymousUser):
    name = u"Anonymous"

login_manager = LoginManager()
login_manager.anonymous_user = Anonymous
login_manager.login_view = "login"
login_manager.login_message = u"Please log in to access this page."
login_manager.refresh_view = "reauth"
login_manager.init_app(app)


@async
def send_async_email(msg):
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


@app.route('/')
def index():
    if current_user.is_authenticated():
        if current_user.get_role() == '1':
            appslist = UserDetail.query \
                                 .filter_by(uid=current_user.get_id()) \
                                 .order_by(db.desc(UserDetail.website))
            return render_template('index.html', appslist=appslist)

    return render_template('welcome.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('manage_apps.html')


@app.route('/add_detail', methods=['GET', 'POST'])
@login_required
def add_detail():
    if current_user.get_role() == '1':
        form = DetailForm()
        if form.validate_on_submit():
            _detail = UserDetail(
                form.name.data,
                form.street.data,
                form.city.data,
                form.phone.data,
                form.website.data,
                date.today(),
                current_user.get_id()
            )
            _detail.date = datetime.now()
            db.session.add(_detail)
            db.session.commit()
            flash(u'Your details were submitted succsessfully.')
            return redirect(url_for('index'))
        return render_template('add_detail.html', form=form)
    return redirect(url_for('index'))

    
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = SignupForm()
    if form.validate_on_submit():
        user = Users(
            form.username.data,
            form.password.data,
            form.email.data,
            1,)
        db.session.add(user)
        db.session.commit()
        confirm_user(form.username.data, form.email.data)
        flash(u'Check your email to activate your account.')
        return redirect(url_for('index'))

    flash(u'Create your flaskCamel account')
    return render_template('register.html', form=form)


def confirm_user(username, email):
    s = URLSafeSerializer('serliaizer_code')
    key = s.dumps([username, email])

    msg = Message("Account Confirmation", sender="your_id@your_host.com", recipients=[email])
    msg.html = "<b>Welcome to flaskCamel!!!</b></br> Confirmation your\
                account by clicking on this below link </br></br> \
                <a href='http://127.0.0.1:5000/confirmaccount/" + key + "'>\
                http://127.0.0.1:5000/confirmaccount/" + key + "</a>\
                </br></br> Team flaskCamel"
    send_async_email(msg)

    flash(u'Confirmation Email sent to: ' + email)
    return redirect(url_for('index'))


@app.route('/confirmaccount/<secretstring>', methods=['GET', 'POST'])
def confirm_account(secretstring):
    s = URLSafeSerializer('serliaizer_code')
    uname, uemail = s.loads(secretstring)
    user = Users.query.filter_by(username=uname).first()
    user.activate = True
    db.session.add(user)
    db.session.commit()
    flash(u'Your account was confirmed succsessfully!!!')
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated():
        return redirect(url_for('index'))
    else:
        form = LoginForm()
        if form.validate_on_submit():
            admin = Users.query.filter_by(username=form.username.data).first()
            if admin:
                if admin.check_password(form.password.data):
                    login_user(admin)
                    flash(admin.username + ' logged in')
                    return redirect(url_for('index'))
                else:
                    flash('wrong pass')
                    return redirect(url_for('login'))
            else:
                flash('wrong username')
                return redirect(url_for('login'))
    flash(u'Enter your email and password.')
    return render_template('login.html', form=form)


@app.route('/passwordreset', methods=['GET', 'POST'])
def reset_password():
    form = PasswordResetForm()
    if form.validate_on_submit():
        if form.username.data:
            user = Users.query.filter_by(username=form.username.data).first()
        elif form.email.data:
            user = Users.query.filter_by(email=form.email.data).first()
        else:
            flash("Username or password doesn't exists")

        if user:
            if user.email:
                s = URLSafeSerializer('serliaizer_code')
                key = s.dumps([user.username, user.email])

            msg = Message("Password reset", sender="your_id@your_host.com", recipients=[user.email])
            msg.html = "<b>Click on this link to reset your password.</b> \
                        #<a href='http://127.0.0.1:5000/passwordreset/ \
                        " + key + "'>http://127.0.0.1:5000/passwordreset/ \
                        " + key + "</a>"

            send_async_email(msg)
            
            flash('Email sent to: ' + user.email)
            return redirect(url_for('reset_password'))
        else:
            flash('No such user')
            return redirect(url_for('reset_password'))
    flash(u'Enter your email or username')
    return render_template('reset_password.html', form=form)


@app.route('/passwordreset/<secretstring>', methods=['GET', 'POST'])
def change_password(secretstring):
    form = PasswordChangeForm()
    if form.validate_on_submit():
      
        if form.password.data:
            s = URLSafeSerializer('serliaizer_code')
            uname, uemail = s.loads(secretstring)
            user = Users.query.filter_by(username=uname).first()
            db.session.add(user)
            user.pwdhash = bcrypt.generate_password_hash(form.password.data)
            db.session.commit()
            flash(u'succsessful password reset')
            return redirect(url_for('login'))
        else:
            flash('Try again!')
            return redirect(url_for('reset_password'))

    return render_template('change_password.html', form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for("index"))


#Facebook OAuth integration

@app.route('/fblogin')
def facebook_login():
    return facebook.authorize(callback=url_for('facebook_authorized',
                              next=request.args.get('next') or request.referrer or None,
                              _external=True))


@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    next_url = request.args.get('next') or url_for('index')
    if resp is None:
        flash('You denied the facebook login')
        return redirect(next_url)

    session['fb_access_token'] = (resp['access_token'], '')

    me = facebook.get('/me')
    user = Users.query.filter_by(fb_id=me.data['id']).first()
    
    if user:
        if me.data['username']:
            fb_username = me.data['username']
        else:
            fb_username = me.data['name']

        fb_email = me.data['email']

        role = 1
        user = Users(fb_username, 'temp', fb_email, role)
        user.fb_id = me.data['id']
        user.activate = True
        user.created = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.uid

        flash('You are now logged in as %s' % user.username)
        return redirect(url_for('index'))


@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('fb_access_token')
