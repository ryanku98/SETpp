from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import UploadForm, LoginForm, RegistrationForm, ChangePasswordForm, RequestPasswordResetForm, SurveyForm
from app.models import User
from app.survey import submitResult
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
import os

# @app.route('/', methods=['GET', 'POST'])
# @app.route('/index', methods=['GET', 'POST'])
@app.route('/')
@app.route('/index')
def index():
    if not current_user.is_authenticated:
        flash('Login to view admin page!')
        return redirect(url_for('login'))
    return render_template('index.html', title='Home')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if User.query.count() != 0:
        flash('Redirected to login page: An admin already exists for this system. Please login for admin privileges.')
        return redirect(url_for('login'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congrats, you are now an admin!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/changepassword', methods=['GET', 'POST'])
def changePassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user or not user.check_password(form.current_password.data):
            flash('email or current password incorrect')
            redirect(url_for('changepassword'))
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        # logout user if logged-in
        if current_user.is_authenticated:
            logout_user()
        flash('Password updated')
        return redirect(url_for('login'))
    return render_template('changePassword.html', title='Change Password', form=form)

@app.route('/requestreset', methods=['GET', 'POST'])
def requestResetPassword():
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        # put reset password code here
        # email user.email 1 time token?
        # https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-x-email-support
        pass
    return render_template('requestPasswordReset.html', title='Reset Password', form=form)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not current_user.is_authenticated:
        flash('Login to view admin page!')
        return redirect(url_for('login'))
    form = UploadForm()
    if form.validate_on_submit():
        f_roster = form.roster.data
        filename = secure_filename(f_roster.filename)
        f_roster.save(os.path.join('documents', 'roster-test.csv'))
        flash('File uploaded!')
        return redirect(url_for('upload'))
    return render_template('upload.html', form=form)

@app.route('/startsurvey')
@login_required
def startSurvey():
    flash('Survey session started')
    return redirect(url_for('index'))

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    form = SurveyForm()
    if form.validate_on_submit():
        submitResult([form.course_id.data, form.learning_1.data, form.learning_2.data, form.learning_3.data, form.learning_4.data, form.learning_5.data, form.learning_6.data, form.lab_1.data, form.lab_2.data, form.lab_3.data, form.lab_4.data, form.lab_5.data, form.lab_6.data, form.spaceequipment_1.data, form.spaceequipment_2.data, form.spaceequipment_3.data, form.spaceequipment_4.data, form.time_1.data, form.time_2.data, form.time_3.data, form.lecture_1.data])
        flash('Survey submitted!')
        return redirect(url_for('survey'))
    return render_template('survey.html', form=form)
