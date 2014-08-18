from datetime import datetime, date
from flask import render_template, url_for, redirect, flash, request
from flask.ext.login import (current_user, login_required)
from flask_debugtoolbar import DebugToolbarExtension
from flaskcamel.forms.base import DetailForm
from flaskcamel import app, db
from flaskcamel.models.base import UserDetail

toolbar = DebugToolbarExtension(app)

# Put your custom

@app.route('/')
def index():
    if current_user.is_authenticated():
        if current_user.get_role() == '1':
            appslist = UserDetail.query.filter_by(
                uid=current_user.get_id()
            ).order_by(
                db.desc(UserDetail.website)
            )
            return render_template('index.html', appslist=appslist)

    return render_template('welcome.html')


@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')


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
