from datetime import datetime
from app import app, db, login
from flask import flash
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
import jwt

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

class Student(db.Model):
    """Defines the Student database model - all created when roster is uploaded"""
    id = db.Column(db.Integer, primary_key=True)
    s_id = db.Column(db.Integer, index=True)
    c_id = db.Column(db.Integer, index=True)
    email = db.Column(db.String(120), index=True)
    def __repr__(self):
        return '<Student {} - ID {} - Course {} - Email {}>'.format(self.id, self.email, self.s_id, self.c_id)

class Section(db.Model):
    """Defines the Section database model - all created when roster is uploaded"""
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(120), index=True)
    course_num = db.Column(db.String(120), index=True)  # catalog number (i.e. 174L)
    course_id = db.Column(db.Integer, index=True, unique=True)
    prof_name = db.Column(db.String(120))
    prof_email = db.Column(db.String(120))
    # links Result objects to a Section object through course_id attribute (result.course_id refers to a Section)
    # results = db.relationship('Result', backref='section', lazy='dynamic')
    def __repr__(self):
        return '<Section {} - {}{} - Course {} - Prof {} - Email {}>'.format(self.id, self.subject, self.course_num, self.course_id, self.prof_name, self.prof_email)

class Result(db.Model):
    """Defines the Result database model - created only when a submission is entered"""
    id = db.Column(db.Integer, primary_key=True)
    # course_id = db.Column(db.Integer, index=True)
    # course_id = db.Column(db.Integer, db.ForeignKey('section.course_id'))
    email = db.Column(db.String(120), index=True)
    response_data = db.Column(db.PickleType)
    def __repr__(self):
        return '<Result {} - Course {} - Prof {}>\n{}'.format(self.id, self.course_id, self.email, self.response_data)

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

def create_reminders(datetimes):
    """Add and commit reminders created from accepted list of datetime objects to the database"""
    Reminder.query.delete()
    for dt in datetimes:
        reminder = Reminder(datetime=dt)
        db.session.add(reminder)
    db.session.commit()
