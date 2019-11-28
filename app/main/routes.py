import os
import csv
from flask import render_template, flash, redirect, url_for, request, current_app
from flask_login import current_user, login_user, logout_user, login_required
from app import db
from app.main import bp
from app.models import User, Student, Section, Result, Deadline, Reminder, log_header, wipeAdmin, wipeSurveyData, studentExists, addResult, addDeadline, addReminders
from app.forms import LoginForm, RegistrationForm, ResetPasswordForm, RequestPasswordResetForm, ChangePasswordForm, CreateSurveyForm, DatesForm, SurveyForm, OverrideForm
from app.survey import parse_roster
from app.emails import send_password_reset_email, send_all_student_emails, send_all_prof_emails
from datetime import datetime

@bp.route('/')
@bp.route('/index')
def index():
    if not current_user.is_authenticated:
        flash('Login to view admin page!')
        return redirect(url_for('main.login'))
    return render_template('index.html', title='Home')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if User.query.count() == 0:
        # redirect to registration page if no admin users
        flash('Redirected to registration page: An admin does not exist for this system. Please register for admin privileges.')
        return redirect(url_for('main.register'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password')
            return redirect(url_for('main.login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign In', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    if User.query.count() > 0:
        flash('Redirected to login page: An admin already exists for this system. If you are the admin, please login for admin privileges.')
        return redirect(url_for('main.login'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congrats, you are now an admin!')
        return redirect(url_for('main.login'))
    return render_template('register.html', title='Register', form=form)

@bp.route('/changePassword', methods=['GET', 'POST'])
@login_required
def changePassword():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        current_user.set_password(form.password.data)
        db.session.add(current_user)
        db.session.commit()
        flash('Password updated')
    return render_template('changePassword.html', title='Change Password', form=form)

@bp.route('/requestreset', methods=['GET', 'POST'])
def requestResetPassword():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RequestPasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Check email for instructions to reset password')
            return redirect(url_for('main.login'))
        else:
            flash('Admin account not found')
    return render_template('requestPasswordReset.html', title='Request Password Reset', form=form)

@bp.route('/resetPassword/<token>', methods=['GET', 'POST'])
def resetPassword(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)     #Decode token, should get id of admin user
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Password updated')
        return redirect(url_for('main.login'))
    return render_template('resetPassword.html', title='Reset Password', form=form)

@bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if not current_user.is_authenticated:
        flash('Login to create survey!')
        return redirect(url_for('main.login'))
    form = CreateSurveyForm()
    if form.validate_on_submit():
        wipeSurveyData()
        parse_roster(form.roster.data)
        # TODO: handle corrupted file uploads
        flash('File uploaded!')
        # set default deadline to a week from upload in case admin doesn't custom input deadline on next page
        addDeadline(datetime.utcnow(), day_offset=7)
        flash('Default deadline set to a week from today')
        # email all students now that roster is uploaded
        return redirect(url_for('main.setDates'))
    return render_template('upload.html', title='Create Survey', form=form)

@bp.route('/deadline', methods=['GET', 'POST'])
def setDates():
    """Set survey deadline and optional student reminders for a survey session"""
    if not current_user.is_authenticated:
        flash('Login to set reminders!')
        return redirect(url_for('main.login'))
    if Section.query.count() == 0:
        flash('No survey session found - please upload valid roster')
        return redirect(url_for('main.index'))
    form = DatesForm()
    # track time on page load for validation purposes
    now = datetime.utcnow()
    if form.validate_on_submit():
        # DatesForm class validates deadline data upon submission
        addDeadline(form.deadline.data)
        addReminders((form.reminder1.data, form.reminder2.data, form.reminder3.data), now)
        return redirect(url_for('main.setDates'))
    return render_template('dates.html', title='Deadline & Reminders', form=form, time=now, defaults=create_defaults(now))

def create_defaults(curr_time):
    """Creates list of datetime strings using values currently in database - for values that don't exist, use current time"""
    # defaults should be a list of defaults for variables in proper string form in the following order: deadline, reminder1, reminder2, reminder3
    defaults = []
    default_format = '%Y-%m-%dT%H:%M'
    deadline = Deadline.query.first()
    if deadline is not None:
        defaults.append(deadline.default_format())
    else:
        defaults.append(curr_time.strftime(default_format))
    reminders = Reminder.query.order_by(Reminder.datetime).all()
    for reminder in reminders:
        defaults.append(str(reminders[0]))
    # fill in to exactly 4 datetimes
    while len(defaults) < 4:
        defaults.append(curr_time.strftime(default_format))
    return defaults

# TODO: remove when done testing
@bp.route('/emailallstudents')
@login_required
def emailallstudents():
    if Student.query.count() >= 1:
        flash('All students emailed')
        # send_all_student_emails() multithreads the actual emailing portion so it no longer blocks until all emails have been sent
        send_all_student_emails()
    else:
        flash('No students found in database - please upload valid roster')
    return redirect(url_for('main.index'))

# TODO: remove when done testing
@bp.route('/emailallprofessors')
@login_required
def emailallprofessors():
    if Section.query.count() >= 1:
        flash('All professors emailed')
        # send_all_prof_emails() multithreads the actual emailing portion so it no longer blocks until all emails have been sent
        send_all_prof_emails()
    else:
        flash('No professors found in database - please upload valid roster')
    return redirect(url_for('main.index'))

@bp.route('/remindallstudents')
@login_required
def remindallstudents():
    if Student.query.count() >= 1:
        flash('All students emailed reminder')
        # send_all_student_emails() multithreads the actual emailing portion so it no longer blocks until all emails have been sent
        send_all_student_emails(reminder=True)
    else:
        flash('No students found in database - please upload valid roster')
    return redirect(url_for('main.index'))

@bp.route('/survey', methods=['GET', 'POST'])
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
        # numerical data has to be type-casted here - WTForms doesn't allow numerical choices (must be str type) but pandas sometimes doesn't properly calculate statistics if entered values are in str form
        response_data = (float(form.learning_1.data), float(form.learning_2.data), float(form.learning_3.data), float(form.learning_4.data), form.learning_5.data, form.learning_6.data, float(form.lab_1.data), float(form.lab_2.data), float(form.lab_3.data), float(form.lab_4.data), float(form.lab_5.data), form.lab_6.data, float(form.spaceequipment_1.data), float(form.spaceequipment_2.data), float(form.spaceequipment_3.data), form.spaceequipment_4.data, float(form.time_1.data), float(form.time_2.data), float(form.time_3.data), form.lecture_1.data)
        addResult(form.student_id.data, form.course_id.data, response_data)
        flash('Survey submitted!')
        return redirect(url_for('main.survey'))
    return render_template('survey.html', title='SET++', form=form, deadline=Deadline.query.first(), time=datetime.utcnow())

@bp.route('/OVERRIDE', methods=['GET', 'POST'])
def override():
    if User.query.count() == 0:
        return redirect(url_for('main.login'))
    form = OverrideForm()
    if form.validate_on_submit():
        if form.password.data == current_app.config['OVERRIDE_PW']:
            print(log_header('OVERRIDE - {}'.format(form.dev_id.data)))
            wipeAdmin()
            flash('Admin data erased')
            wipeSurveyData()
            flash('Survey data erased')
            return redirect(url_for('main.register'))
        else:
            flash('Incorrect password')
    return render_template('override.html', title='DEVELOPER OVERRIDE', form=form)

