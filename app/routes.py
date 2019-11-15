import os
import csv
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.models import User, Student, Section, Result, Deadline, Reminder, log_header, wipeDatabase, studentExists, addResult, addDeadline, addReminders
from app.forms import LoginForm, RegistrationForm, ResetPasswordForm, RequestPasswordResetForm, ChangePasswordForm, CreateSurveyForm, DatesForm, SurveyForm
from app.survey import parse_roster
from app.emails import send_password_reset_email, send_all_student_emails, send_all_prof_emails
from datetime import datetime
from threading import Thread

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
        db.session.commit()
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
    return render_template('requestPasswordReset.html', title='Request Password Reset', form=form)

@app.route('/createsurvey', methods=['GET', 'POST'])
def createSurvey():
    if not current_user.is_authenticated:
        flash('Login to create survey!')
        return redirect(url_for('login'))
    form = CreateSurveyForm()
    if form.validate_on_submit():
        # clear old roster and results
        wipeDatabase()
        # TODO: make multithreaded
        # saveRoster(form.roster.data)
        parse_roster(form.roster.data)

        # f_roster = form.roster.data
        # filename = secure_filename(f_roster.filename)
        # f_roster.save(os.path.join('documents', filename))
        # # convert to CSV if Excel file
        # f_roster = convertToCSV(os.path.join('documents', filename))

        # Thread(target=parse_roster).start()
        flash('File uploaded!')
        # set default deadline to a week from upload in case admin doesn't custom input deadline on next page
        addDeadline(datetime.utcnow(), day_offset=7)
        return redirect(url_for('setDates'))
    return render_template('createSurvey.html', title='Create Survey', form=form)

@app.route('/deadline', methods=['GET', 'POST'])
def setDates():
    """Set survey deadline and optional student reminders for a survey session"""
    if not current_user.is_authenticated:
        flash('Login to set reminders!')
        return redirect(url_for('login'))
    form = DatesForm()
    # track time on page load for validation purposes
    curr_time = datetime.utcnow()
    if form.validate_on_submit():
        # DatesForm class validates deadline data upon submission
        addDeadline(form.deadline.data)
        addReminders([form.reminder1.data, form.reminder2.data, form.reminder3.data], now)
        return redirect(url_for('setDates'))
    return render_template('dates.html', title='Deadline & Reminders', form=form, time=curr_time, defaults=create_defaults(curr_time))

def create_defaults(curr_time):
    """Creates list of datetime strings using values currently in database - for values that don't exist, use current time"""
    # defaults should be a list of defaults for variables in proper string form in the following order: deadline, reminder1, reminder2, reminder3
    default_format = '%Y-%m-%dT%H:%M'
    defaults = []
    deadline = Deadline.query.first()
    if deadline is not None:
        defaults.append(deadline.default_format())
    else:
        defaults.append(curr_time.strftime(default_format))
    reminders = Reminder.query.all()
    for reminder in reminders:
        defaults.append(str(reminders[0]))
    # fill in to exactly 3 datetimes
    while len(defaults) < 4:
        defaults.append(curr_time.strftime(default_format))
    return defaults

# TODO: remove when done testing
@app.route('/startsurvey')
@login_required
def startSurvey():
    flash('Survey session started')
    send_all_student_emails()
    return redirect(url_for('index'))

# TODO: remove when done testing
@app.route('/sendAnalytics')
@login_required
def sendAnalytics():
    send_all_prof_emails()
    flash('Analytics Sent')
    return redirect(url_for('index'))

@app.route('/sendReminder')
@login_required
def sendReminder():
    send_all_student_emails()
    flash('Reminder Emails Sent')
    return redirect(url_for('index'))

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    form = SurveyForm()
    if request.method == 'GET':
        s_id = request.args.get('s')
        c_id = request.args.get('c')
        # pre-fill student ID and course only if valid (avoids accidental tampering)
        # avoids false presumption by user that prefilled data MUST be accurate
        if s_id and c_id and studentExists(s_id, c_id):
            form.student_id.data = s_id
            form.course_id.data = c_id
    if form.validate_on_submit():
        response_data = [form.learning_1.data, form.learning_2.data, form.learning_3.data, form.learning_4.data, form.learning_5.data, form.learning_6.data, form.lab_1.data, form.lab_2.data, form.lab_3.data, form.lab_4.data, form.lab_5.data, form.lab_6.data, form.spaceequipment_1.data, form.spaceequipment_2.data, form.spaceequipment_3.data, form.spaceequipment_4.data, form.time_1.data, form.time_2.data, form.time_3.data, form.lecture_1.data]
        addResult(form.student_id.data, form.course_id.data, response_data)
        flash('Survey submitted!')
        return redirect(url_for('survey'))
    return render_template('survey.html', title='SET++', form=form, deadline=Deadline.query.first(), time=datetime.utcnow())
