from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, ResetPasswordForm, RequestPasswordResetForm, ChangePasswordForm, CreateSurveyForm, DatesForm, SurveyForm
# CHANGE WHEN FUNCTION IS MOVED:
from app.forms import is_valid_datetime
from datetime import datetime

from app.models import User
from app.survey import submitResult, roster_file, clearSurveySession, convertToCSV, studentExists
from app.emails import send_password_reset_email, send_all_student_emails
# from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
import os

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

@app.route('/changePassword', methods=['GET', 'POST'])
def changePassword():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.current_password.data):
            current_user.set_password(form.password.data)
            db.session.add(current_user)
            db.session.commit()
            #logout user if logged-in
            if current_user.is_authenticated:
                logout_user()
            flash('Password updated')
        else:
            flash('Incorrect password')
            return redirect(url_for('changePassword'))
    return render_template('changePassword.html', title='Change Password', form=form)

@app.route('/resetPassword/<token>', methods=['GET', 'POST'])
def resetPassword(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)     #Decode token, should get id of admin user
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        # logout user if logged-in
        if current_user.is_authenticated:
            logout_user()
        flash('Password updated')
        return redirect(url_for('login'))
    return render_template('resetPassword.html', title='Reset Password', form=form)

@app.route('/requestreset', methods=['GET', 'POST'])
def requestResetPassword():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)     #invokes function defined in emails.py
        flash('Check email for instructions to reset password')
        return redirect(url_for('login'))
    return render_template('requestPasswordReset.html', title='Reset Password', form=form)

@app.route('/createsurvey', methods=['GET', 'POST'])
def createSurvey():
    if not current_user.is_authenticated:
        flash('Login to create survey!')
        return redirect(url_for('login'))
    form = CreateSurveyForm()
    if form.validate_on_submit():
        # clear old roster and results
        clearSurveySession()
        f_roster = form.roster.data
        filename = secure_filename(f_roster.filename)
        f_roster.save(os.path.join('documents', filename))
        # convert to CSV if Excel file
        f_roster = convertToCSV(os.path.join('documents', filename))
        flash('File uploaded!')
        # TODO: set default survey deadline to a week from upload in case admin doesn't custom input deadline
        # TODO: do we want default reminders?
        return redirect(url_for('deadline'))
    return render_template('createSurvey.html', form=form)

@app.route('/deadline', methods=['GET', 'POST'])
def setDates():
    """Set survey deadline and optional student reminders for a survey session"""
    if not current_user.is_authenticated:
        flash('Login to set reminders!')
        return redirect(url_for('login'))
    # track time on page load for validation purposes
    curr_time = datetime.utcnow()
    form = DatesForm()
    if form.validate_on_submit():
        flash('Deadline set for ' + form.deadline.data.strftime(form.display_format))
        if is_valid_datetime(form.reminder1.data, curr_time):
            flash('Reminder 1 set for ' + form.reminder1.data.strftime(form.display_format))
        if is_valid_datetime(form.reminder2.data, curr_time):
            flash('Reminder 2 set for ' + form.reminder2.data.strftime(form.display_format))
        if is_valid_datetime(form.reminder3.data, curr_time):
            flash('Reminder 3 set for ' + form.reminder3.data.strftime(form.display_format))
        return redirect(url_for('setDates'))
    return render_template('dates.html', form=form, time=curr_time)

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    form = SurveyForm()
    if request.method == 'GET':
        s_id = request.args.get('s')
        c_id = request.args.get('c')
        # pre-fill student ID and course # if valid (avoids accidental tampering)
        # also avoids false presumption by user that prefilled data MUST be accurate
        if s_id and c_id and studentExists(s_id, c_id):
            form.student_id.data = s_id
            form.course_id.data = c_id
    if form.validate_on_submit():
        submitResult([form.course_id.data, form.learning_1.data, form.learning_2.data, form.learning_3.data, form.learning_4.data, form.learning_5.data, form.learning_6.data, form.lab_1.data, form.lab_2.data, form.lab_3.data, form.lab_4.data, form.lab_5.data, form.lab_6.data, form.spaceequipment_1.data, form.spaceequipment_2.data, form.spaceequipment_3.data, form.spaceequipment_4.data, form.time_1.data, form.time_2.data, form.time_3.data, form.lecture_1.data])
        flash('Survey submitted!')
        return redirect(url_for('survey'))
    return render_template('survey.html', form=form)
