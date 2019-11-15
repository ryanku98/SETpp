import os
import jwt
import pandas
from app import app, db, login
from flask import flash, url_for
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from time import time
from datetime import datetime as DT
from dateutil.relativedelta import relativedelta

def log_header(title):
    """Simple function to return a string of a title surrounded by dashes to represent a distinct section of log outputs"""
    if len(title) == 0:
        return '----------------------------------------------------------------------'
    while len(title) < 70:
        if len(title) % 2 == 0:
            title = '-' + title
        else:
            title = title + '-'
    return title

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

def wipeDatabase():
    """Deletes all files and database objects related to last survey session"""
    Section.query.delete()
    Student.query.delete()
    Result.query.delete()
    Deadline.query.delete()
    Reminder.query.delete()

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
    def get_means(self):
        """This function uses Pandas to analyze means of the responses linked to this Section instance"""
        responses = []
        for result in self.results.all():
            responses.append(result.response_data)
        df = pandas.DataFrame(responses, column=getQuestionsList())    # dataframe
        means = df.mean().items()    # zip of data means
        return remove_frqs(means)

    def get_stds(self):
        """This function uses Pandas to analyze standard deviations of the responses linked to this Section instance"""
        responses = []
        for result in self.results.all():
            responses.append(result.response_data)
        df = pandas.DataFrame(responses, column=getQuestionsList())    # dataframe
        means = df.std().items()    # zip of data stds
        return remove_frqs(means)

    def frq_responses(self):
        """
        This function returns a list of responses for the FRQs
        This format of the returned values should be a tuple of tuples as follows:
                Q1 = 'Ways to say hi';  Q2 = 'Ways to say bye'
                A_a1 = 'Hi';            A_a2 = 'Bye'
                A_b1 = 'Hello';         A_b2 = 'Byebye'
                responses_tuple = ( (Q1, (A_a1, A_b1) ), (Q2, (A_a2, A_b2) ) )
                -->
                responses_tuple = (('Ways to say hi', ('Hi', 'Hello')), ('Ways to say bye', ('Bye', 'Byebye')))
        To retrieve specific values:
                print('responses_tuple: {}'.format(responses_tuple))
                for x, question_tuple in enumerate(responses_tuple):
                    print('\tquestion_tuple {}: {}'.format(x, question_tuple))
                    answer_tuple = question_tuple[1]    # 1 is *mandatory* not example because the answer_tuple is always the 1st (index)/2nd (object) of the question_tuple
                    print('\tanswers_tuple {}: {}'.format(x, answer_tuple))
                    for y, answer in enumerate(answer_tuple):
                        print('\t\tanswer {}-{}: {}'.format(x, y, answer))
            # this loop should print the following
        >>> responses_tuple: (('Ways to say hi', ('Hi', 'Hello')), ('Ways to say bye', ('Bye', 'Byebye')))
        >>>     question_tuple 0: ('Ways to say hi', ('Hi', 'Hello'))
        >>>     answers_tuple 0: ('Hi', 'Hello')
        >>>         answer 0-0: Hi
        >>>         answer 0-1: Hello
        >>>     question_tuple 1: ('Ways to say bye', ('Bye', 'Byebye'))
        >>>     answers_tuple 1: ('Bye', 'Byebye')
        >>>         answer 1-0: Bye
        >>>         answer 1-1: Byebye
        """
        responses_tuple = []    # will be converted to tuple later
        results = self.results.query.all()
        for i, question in enumerate(getQuestionsList()):
            # if index corresponds to an FRQ
            if 'free text response' in question.lower():
                answers_tuple = []  # will be converted to tuple later
                # add responses for question i to a list
                for result in results:
                    answers.append(result.response_data[i])
                # question_tuple = (question, tuple(answers_tuple))
                # responses_tuple.append(question_tuple)
                responses_tuple.append((question, tuple(answer_tuple)))
        return tuple(responses_tuple)

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

def remove_frqs(zip_obj):
    """Ensures no FRQ responses get added to dataframe calculations"""
    # this is required for a severe edge case when an FRQ of every result happens to be numbers only
    indices, items = zip(*zip_obj)
    indices = list(indices)
    items = list(items)
    questions = getQuestionsList()
    frqs = []   # list of frqs that showed up
    for i in indices:
        if 'free text response' in questions[i].lower():
            frqs.append(i)
    for i in frqs:
        indices.pop(i)
        items.pop(i)
    # items is now a list of dataframe values corresponding to only numerical inputs of the survey form
    return items

def getQuestionsList():
    with open(os.path.join('documents', 'survey_questions.txt'), 'r') as f_questions:
        headers = f_questions.readlines()
    # strip trailing newline character that shows up for unknown reason
    for i, header in enumerate(headers):
        headers[i] = header.rstrip('\n')
    return headers

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
    def get_survey_link(self):
        return url_for('survey', s=self.s_id, c=self.c_id, _external=True)
    def __repr__(self):
        return '<Student ID {} - Course {} - Email {}>'.format(self.s_id, self.c_id, self.email)

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
        return '<Result Course {} - Data: {}>'.format(self.course_id, self.response_data)

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
    datetime = db.Column(db.DateTime, index=True, default=DT.utcnow())
    def update_datetime(self, dt):  # assume entered dt is valid
        self.datetime = dt
    def get_datetime(self): # more legible, American format
        return '{} UTC'.format(self.datetime.strftime('%m-%d-%Y %H:%M'))
    def is_valid(self, now=DT.utcnow()):
        return is_valid_datetime(self.datetime, now)
    def default_format(self):
        return self.datetime.strftime('%Y-%m-%dT%H:%M')
    def __repr__(self):
        return '<Deadline {} UTC>'.format(self.default_format())

def addDeadline(dt, day_offset=0, hour_offset=0):
    """Adds/Updates the Deadline in the database - there should always at most be only one"""
    new_time = dt + relativedelta(days=day_offset, hours=hour_offset)
    deadline = Deadline.query.first()
    if deadline is not None:
        deadline.update_datetime(new_time)
    else:
        deadline = Deadline(datetime=new_time)
        db.session.add(deadline)
    db.session.commit()
    print('ADDED: {}'.format(deadline))

class Reminder(db.Model):
    """Defines the Reminder database model - for this application, at most 3 Reminders should exist at any given time"""
    id = db.Column(db.Integer, primary_key=True)
    datetime = db.Column(db.DateTime, index=True, default=DT.utcnow())
    def update_datetime(self, dt):  # assume entered dt is valid
        self.datetime = dt
    def get_datetime(self): # more legible, American format
        return '{} UTC'.format(self.datetime.strftime('%m-%d-%Y %H:%M'))
    def is_valid(self, now=DT.utcnow()):
        return is_valid_datetime(self.datetime, now)
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

def is_valid_datetime(dt1, dt2):
    """Returns True if dt1 is strictly after dt2 - False otherwise (is before or exactly equal)"""
    # at least one attribute of delta is positive iff dt1 is in fact after dt2 (non-positive attributes are 0)
    # all attributes of delta are 0 iff dt1 is identical to dt2
    # at least one attribute of delta is negative iff dt1 is before dt2 (non-negative attributes are 0)
    delta = relativedelta(dt1, dt2)
    # test for negativity in attributes:
    # first assume invalid
    # if hit positive value, set flag to True but continue to end
    # if hit negative value, return False immediately and unconditionally
    # if/when reached end, return flag (if all 0s, flag remains False)
    validity = False
    delta_attributes = [delta.years, delta.months, delta.weeks, delta.days, delta.hours, delta.minutes, delta.seconds, delta.microseconds]
    for attribute in delta_attributes:
        # if positive
        if attribute > 0:
            validity = True
        # if negative
        elif attribute < 0:
            return False
    return validity
