from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, IntegerField, RadioField, TextAreaField
from wtforms.ext.dateutil.fields import DateTimeField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
from flask_wtf.file import FileRequired, FileAllowed
from app.models import User, Section, Student, Result, Deadline, Reminder, is_valid_datetime
from datetime import datetime

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    # Flask custom validators run when form.validate_on_submit() is called in routes.py,
    # but this requires validate_<attribute>(self, <attribute>) format
    # so this is just a small hack to integrate short custom validators
    def validate_email(self, email):
        if User.query.count() != 0:
            raise ValidationError('An admin already exists for this system.')

class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    password = PasswordField('New Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Change password')

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Request Password Reset')

class RequestPasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset')

class CreateSurveyForm(FlaskForm):
    roster = FileField(validators=[FileRequired(), FileAllowed(['csv', 'xlsx', 'xls'], 'CSV/Excel files only!')])
    submit = SubmitField('Create')

class DatesForm(FlaskForm):
    parse_kwargs = {'yearfirst': True, 'dayfirst': False}
    display_format = '%m/%d/%Y %H:%M'
    render_kw = {'type': 'datetime-local'}
    deadline = DateTimeField('Survey deadline', parse_kwargs=parse_kwargs, display_format=display_format, render_kw=render_kw, validators=[DataRequired()])
    reminder1 = DateTimeField('First student reminder (optional)', parse_kwargs=parse_kwargs, display_format=display_format, render_kw=render_kw)
    reminder2 = DateTimeField('Second student reminder (optional)', parse_kwargs=parse_kwargs, display_format=display_format, render_kw=render_kw)
    reminder3 = DateTimeField('Third student reminder (optional)', parse_kwargs=parse_kwargs, display_format=display_format, render_kw=render_kw)
    submit = SubmitField('Save')

    def validate_deadline(self, deadline):
        # compare submitted deadline to current time
        if not is_valid_datetime(self.deadline.data, datetime.utcnow()):
            raise ValidationError('Invalid deadline: make sure to set a deadline after the current time')

class SurveyForm(FlaskForm):
    # SUBMISSION VALIDATION
    student_id = IntegerField('Student ID # (For verification purposes only - your submission is completely anonymous)', validators=[DataRequired()])
    course_id = IntegerField('Lab Section #', validators=[DataRequired()])

    # SURVEY QUESTIONS
    text_area_size = {'rows':3,'cols':80}
    scale_choices = [('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5')]
    time_choices = [('1.5','<2'), ('2','2'), ('2.5','2.5'), ('3','3'), ('3.5','>3')]
    max_length = 2000
    # TODO: fix time values to be officially entered as integers for proper data analysis
    learning_1 = RadioField('The labs helped me understand the lecture material. (An answer of 3 is neutral)', choices=scale_choices, validators=[DataRequired()])
    learning_2 = RadioField('The labs taught me new skills. (An answer of 3 is neutral)', choices=scale_choices, validators=[DataRequired()])
    learning_3 = RadioField('The labs taught me to think creatively. (An answer of 3 is neutral)', choices=scale_choices, validators=[DataRequired()])
    learning_4 = RadioField('I would be able to repeat the labs without help. (An answer of 3 is neutral)', choices=scale_choices, validators=[DataRequired()])
    learning_5 = TextAreaField('What was your favorite aspect of the lab?', render_kw=text_area_size, validators=[DataRequired(), Length(min=1, max=max_length, message='{} character limit.'.format(max_length))])
    learning_6 = TextAreaField('What was your favorite aspect of the lab?', render_kw=text_area_size, validators=[DataRequired(), Length(min=1, max=max_length, message='{} character limit.'.format(max_length))])
    lab_1 = RadioField('The lab instructor was supportive. (An answer of 3 is neutral)', choices=scale_choices, validators=[DataRequired()])
    lab_2 = RadioField('The lab instructor was approachable. (An answer of 3 is neutral)', choices=scale_choices, validators=[DataRequired()])
    lab_3 = RadioField('The lab instructor was able to answer my questions. (An answer of 3 is neutral)', choices=scale_choices, validators=[DataRequired()])
    lab_4 = RadioField('The lab instructor helped me reach a clear understanding of key concepts. (An answer of 3 is neutral)', choices=scale_choices, validators=[DataRequired()])
    lab_5 = RadioField('The lab instructor fostered a mutually respectful learning environment. (An answer of 3 is neutral)', choices=scale_choices, validators=[DataRequired()])
    lab_6 = TextAreaField('What, if anything, could the lab instructor do to improve the experience?', render_kw=text_area_size, validators=[DataRequired(), Length(min=1, max=max_length, message='{} character limit.'.format(max_length))])
    spaceequipment_1 = RadioField('The amount of lab equipment was sufficient. (An answer of 3 is neutral)', choices=scale_choices, validators=[DataRequired()])
    spaceequipment_2 = RadioField('The available space was sufficient for the lab activities. (An answer of 3 is neutral)', choices=scale_choices, validators=[DataRequired()])
    spaceequipment_3 = RadioField('If lab equipment or setups were not functioning properly, adequate support was available to rectify the situation. (An answer of 3 is neutral)', choices=scale_choices, validators=[DataRequired()])
    spaceequipment_4 = TextAreaField('What, if anything, could improve lab space and equipment?', render_kw=text_area_size, validators=[DataRequired(), Length(min=1, max=max_length, message='{} character limit.'.format(max_length))])
    time_1 = RadioField('On average, the approximate number of hours completing a lab was', choices=time_choices, validators=[DataRequired()])
    time_2 = RadioField('How many hours did you spend preparing for the lab?', choices=time_choices, validators=[DataRequired()])
    time_3 = RadioField('How many hours did you spend writing lab reports outside the designated lab period?', choices=time_choices, validators=[DataRequired()])
    lecture_1 = TextAreaField('What feedback would you give the lecture section instructor (not the lab TA) about the labs?', render_kw=text_area_size, validators=[DataRequired(), Length(min=1, max=max_length, message='{} character limit.'.format(max_length))])

    submit = SubmitField('Submit')

    # Flask custom validators run when form.validate_on_submit() is called in routes.py,
    # but this requires validate_<attribute>(self, <attribute>) format
    # so this is just a small hack to integrate short custom validators
    def validate_course_id(self, course_id):
        student = Student.query.filter_by(s_id=self.student_id.data, c_id=self.course_id.data).first()
        if student is None:
            raise ValidationError('Matching student ID and lab section number not found on roster, please try again.')
        elif student.survey_submitted:
            raise ValidationError('Database indicates this student has already submitted a survey for lab section {}.'.format(student.c_id))

    # TODO: make sure this executes/validates properly - still unsure
    def validate_submit(self, submit):
        deadline = Deadline.query.first()
        if deadline is not None and not deadline.is_valid():
            raise ValidationError('Sorry, the deadline for this survey session has already passed.')

