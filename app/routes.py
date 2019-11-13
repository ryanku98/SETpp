from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from app import app, db
from app.forms import LoginForm, RegistrationForm, ResetPasswordForm, RequestPasswordResetForm, ChangePasswordForm, CreateSurveyForm, DatesForm, SurveyForm
from app.models import User, Student, Section, Result, Deadline, Reminder, create_reminders
from app.survey import submitResult, roster_file, clearSurveySession, convertToCSV, studentExists, is_valid_datetime
from app.emails import send_password_reset_email, send_all_student_emails, send_all_prof_emails
from datetime import datetime
from werkzeug.utils import secure_filename
import os
import csv
from app.survey import roster_filepath, s_id_i_roster, c_id_i_roster, prof_email_i_roster, stud_email_i_roster, subject_i_roster, course_i_roster, prof_name_i_roster
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
        # print(form.roster.data)
        # convert to CSV if Excel file
        f_roster = convertToCSV(os.path.join('documents', filename))

        # TODO: make multithreaded
        # parse_roster()
        Thread(target=parse_roster).start()
        # TODO: set default survey deadline to a week from upload in case admin doesn't custom input deadline
        flash('File uploaded!')
        return redirect(url_for('setDates'))
    return render_template('createSurvey.html', form=form)

def parse_roster():
    """Use uploaded roster to create students and sections in database - should be called *immediately* after roster is uploaded"""
    with open(roster_filepath, 'r', newline='') as f_roster:
        # skip header row
        next(f_roster)
        # set of tuples that represent sections
        # using tuples instead of immediately creating them because every new Section object created is seen as different, even if it holds the same information
        sections = set()
        rows = csv.reader(f_roster, delimiter=',')
        for row in rows:
            # make one student per row
            s_id = row[s_id_i_roster].lstrip('0').rstrip('.0')
            c_id = row[c_id_i_roster].lstrip('0').rstrip('.0')
            stud_email = row[stud_email_i_roster]
            db.session.add(Student(s_id=s_id, c_id=c_id, email=stud_email))

            # make one section per row, set object type eliminates repeats
            subject = row[subject_i_roster]
            course_num = row[course_i_roster]
            prof_name = row[prof_name_i_roster]
            prof_email = row[prof_email_i_roster]
            sections.add((subject, course_num, c_id, prof_name, prof_email))
            # sections.add(Section(subject=subject, course=course, course_id=c_id, prof_name=prof_name, prof_email=prof_email))

    for s in sections:
        db.session.add(Section(subject=s[0], course_num=s[1], course_id=s[2], prof_name=s[3], prof_email=s[4]))

    print('Students and Sections added to database')
    db.session.commit()

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
        deadline = Deadline.query.first()
        # if a deadline already exists
        # NOTE: a deadline should always exist, but this is a failsafe to avoid extraneous/unforeseen errors
        if deadline is not None:
            deadline.update_datetime(form.deadline.data)
        else:
            db.session.add(Deadline(datetime=form.deadline.data))
        flash('Deadline set for ' + str(deadline))
        db.session.commit()

        # add valid reminders to 'reminders' set (should be datetime objects)
        reminders = set()
        if is_valid_datetime(form.reminder1.data, curr_time):
            reminders.add(form.reminder1.data)
        if is_valid_datetime(form.reminder2.data, curr_time):
            reminders.add(form.reminder2.data)
        if is_valid_datetime(form.reminder3.data, curr_time):
            reminders.add(form.reminder3.data)
        # add and commit 'reminders' set to database
        create_reminders(reminders)
        for reminder in reminders:
            flash('Reminder set for ' + str(reminder))
        return redirect(url_for('setDates'))
    return render_template('dates.html', form=form, time=curr_time, defaults=create_defaults(curr_time))

def create_defaults(curr_time):
    """Creates list of datetime strings using values currently in database - for values that don't exist, use current time"""
    # defaults should be a list of defaults for variables in proper string form in the following order: deadline, reminder1, reminder2, reminder3
    default_format = '%Y-%m-%dT%H:%M'
    defaults = []
    deadline = Deadline.query.first()
    if deadline is not None:
        defaults.append(str(deadline))
    else:
        defaults.append(curr_time.strftime(default_format))
    myquery = Reminder.query.all()
    if len(myquery) >= 1:
        defaults.append(str(myquery[0]))
    else:
        defaults.append(curr_time.strftime(default_format))
    if len(myquery) >= 2:
        defaults.append(str(myquery[1]))
    else:
        defaults.append(curr_time.strftime(default_format))
    if len(myquery) >= 3:
        defaults.append(str(myquery[2]))
    else:
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
        # pre-fill student ID and course # if valid (avoids accidental tampering)
        # also avoids false presumption by user that prefilled data MUST be accurate
        if s_id and c_id and studentExists(s_id, c_id):
            form.student_id.data = s_id
            form.course_id.data = c_id
    if form.validate_on_submit():
        # submitResult(form.course_id.data, [form.learning_1.data, form.learning_2.data, form.learning_3.data, form.learning_4.data, form.learning_5.data, form.learning_6.data, form.lab_1.data, form.lab_2.data, form.lab_3.data, form.lab_4.data, form.lab_5.data, form.lab_6.data, form.spaceequipment_1.data, form.spaceequipment_2.data, form.spaceequipment_3.data, form.spaceequipment_4.data, form.time_1.data, form.time_2.data, form.time_3.data, form.lecture_1.data])
        response_data = [form.learning_1.data, form.learning_2.data, form.learning_3.data, form.learning_4.data, form.learning_5.data, form.learning_6.data, form.lab_1.data, form.lab_2.data, form.lab_3.data, form.lab_4.data, form.lab_5.data, form.lab_6.data, form.spaceequipment_1.data, form.spaceequipment_2.data, form.spaceequipment_3.data, form.spaceequipment_4.data, form.time_1.data, form.time_2.data, form.time_3.data, form.lecture_1.data]
        try:
            section = Section.query.filter_by(course_id=c_id).first()
            # db.session.add(Result(section=section, response_data=response_data))
        except:
            pass
        flash('Survey submitted!')
        return redirect(url_for('survey'))
    return render_template('survey.html', form=form)
