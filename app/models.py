from datetime import datetime
from app import app, db, login
from flask import flash, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
import jwt

def log_added(obj):
    """Simple universal logging function to standarize log messages for added database objects"""
    print('ADDED {}'.format(obj))

# inherits from db.Model, a base class for all models in Flask-SQLAlchemy
class User(UserMixin, db.Model):
    """Defines the User database model - for this instance, at most 1 User should exist at any given time"""
    # defines fields as class variables, or instances of db.Column class, taking field type as an argument
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    def __repr__(self):
        return '<User {}>'.format(self.email)
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    def get_reset_password_token(self, expires_in=600): #Encodes {info} and returns a token
        return jwt.encode({'reset_password': self.id, 'exp': time() + expires_in}, app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')
    def verify_reset_password_token(token): #Decodes token using SECRET_KEY defined in app config class
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'], algorithm=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Section(db.Model):
    """Defines the Section database model - all created when roster is uploaded"""
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(120))
    course_num = db.Column(db.String(120))  # catalog number (i.e. 174L)
    course_id = db.Column(db.Integer, index=True, unique=True)
    prof_name = db.Column(db.String(120))
    prof_email = db.Column(db.String(120))
    # links Student objects to a Section object through section attribute (student.section refers to a Section)
    students = db.relationship('Student', backref='section', lazy='dynamic')
    # links Result objects to a Section object through section attribute (result.section refers to a Section)
    results = db.relationship('Result', backref='section', lazy='dynamic')
    def __repr__(self):
        return '<Section Course {}>'.format(self.course_id)

def addSection(subject, course_num, course_id, prof_name, prof_email):
    section = Section.query.filter_by(course_id=course_id).first()
    if section is None:
        section = Section(subject=subject, course_num=course_num, course_id=course_id, prof_name=prof_name, prof_email=prof_email)
        db.session.add(section)
        db.session.commit()
        log_added(section)
    # the following cases (theoretically) should not happen if the roster is properly ordered by course ID
    else:
        print('ERROR: {} cannot be added - already exists'.format(section))

class Student(db.Model):
    """Defines the Student database model - all created when roster is uploaded"""
    id = db.Column(db.Integer, primary_key=True)
    s_id = db.Column(db.Integer, index=True)
    email = db.Column(db.String(120))
    # has section attribute linked to corresponding Section object
    submitted = db.Column(db.Boolean, default=False)
    c_id = db.Column(db.Integer, db.ForeignKey('section.course_id'))
    def submitted(self):
        self.submitted = True
    def __repr__(self):
        return '<Student ID {} - Course {}>'.format(self.s_id, self.c_id)

def addStudent(s_id, c_id, email):
    """Function to add student, ensures no repeats (same student ID and course ID)"""
    section = Section.query.filter_by(course_id=c_id).first()
    student = Student.query.filter_by(s_id=s_id, c_id=c_id).first()
    if section is not None and student is None:
        student = Student(section=section, s_id=s_id, email=email)
        db.session.add(student)
        db.session.commit()
        log_added(student)
    # the following cases (theoretically) should not happen if the roster is logically correct
    elif student is not None:
        print('ERROR: {} cannot be added - already exists'.format(student))
    elif section is None:
        print('ERROR: <Student ID {} - Course {}> cannot be added - section {} does not exist'.format(s_id, c_id, c_id))

# TODO: check if still needed? remove if unnecessary
def studentExists(s_id, c_id):
    """Checks if student of matching student ID and course ID exists in the database"""
    if Student.query.filter_by(s_id=s_id, c_id=c_id).count() == 0:
        return False
    return True

class Result(db.Model):
    """Defines the Result database model - created only when a submission is entered"""
    id = db.Column(db.Integer, primary_key=True)
    response_data = db.Column(db.PickleType)
    # has section attribute linked to corresponding Section object
    course_id = db.Column(db.Integer, db.ForeignKey('section.course_id'))
    def __repr__(self):
        return '<Result Course {}>\n{}'.format(self.course_id, self.response_data)

def addResult(s_id, c_id, response_data):
    section = Section.query.filter_by(course_id=form.course_id.data).first()
    student = Student.query.filter_by(s_id=s_id, c_id=c_id).first()
    if section is not None:
        result = Result(section=section, response_data=response_data)
        if student is not None and not student.submitted:
            student.submitted()
            db.session.add(result)
            db.session.commit()
            log_added(result)
    # the following cases (theoretically) should not happen if the form properly validates
        elif student is None:
            print('ERROR: {} cannot be added - <Student ID {} - Course {}> does not exist'.format(result, s_id, c_id))
        elif student.submitted:
            print('ERROR: {} cannot be added - {} already submitted'.format(result, student))
    elif section is None:
        # should DEFINITELY never happen if student with submitted credentials can be found as per form validation
        print('ERROR: <Result Course {}> cannot be added - section {} does not exist'.format(c_id, c_id))

class Deadline(db.Model):
    """Defines the Deadline database model - for this instance, at most 1 Deadline should exist at any given time"""
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    def update_datetime(self, dt):
        # assume entered dt is valid
        self.datetime = dt
    def __str__(self):
        return self.datetime.strftime('%Y-%m-%dT%H:%M')
    def __repr__(self):
        return '<Deadline {}>'.format(str(self))

def addDeadline(dt):
    """Adds/Updates the Deadline in the database - there should always at most be only one"""
    deadline = Deadline.query.first()
    if deadline is not None:
        deadline.update_datetime(dt)
    else:
        deadline = Deadline(datetime=dt)
        db.session.add(deadline)
    db.session.commit()
    print('ADDED: {}'.format(deadline))

class Reminder(db.Model):
    """Defines the Reminder database model - for this application, at most 3 Reminders should exist at any given time"""
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    def update_datetime(self, dt):
        # assume entered dt is valid
        self.datetime = dt
    def __str__(self):
        return self.datetime.strftime('%Y-%m-%dT%H:%M')
    def __repr__(self):
        return '<Reminder {}>'.format(str(self))

def addReminders(datetime_list, now):
    """Wipe database of Reminder objects and add valid datetimes from inputted list without repeats"""
    Reminder.query.delete()
    for dt in datetime_list:
        if is_valid_datetime(dt, now) and Reminder.query.filter_by(datetime=dt).count() == 0:
            reminder = Reminder(datetime=dt)
            db.session.add(reminder)
            print('ADDED: {}'.format(reminder))
    db.session.commit()
