from flask_wtf import FlaskForm
from wtforms import FileField, StringField, PasswordField, BooleanField, SubmitField, IntegerField, RadioField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError
from flask_wtf.file import FileRequired, FileAllowed
from app.models import User
from app.survey import studentExists

class UploadForm(FlaskForm):
    roster = FileField(validators=[FileRequired(), FileAllowed(['csv', 'xlsx', 'xls'], 'CSV/Excel files only!')])
    submit = SubmitField('Upload')

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

class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat New Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reqest Password Reset')

class RequestPasswordResetForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Reset')

class SurveyForm(FlaskForm):
    # SUBMISSION VALIDATION
    student_id = StringField('Student ID #', validators=[DataRequired()])
    course_id = IntegerField('Lab Course #', validators=[DataRequired()])

    # SURVEY QUESTIONS
    learning_1 = RadioField('The labs helped me understand the lecture material. (An answer of 3 is neutral)', choices=[('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5')], validators=[DataRequired()])
    learning_2 = RadioField('The labs taught me new skills. (An answer of 3 is neutral)', choices=[('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5')], validators=[DataRequired()])
    learning_3 = RadioField('The labs taught me to think creatively. (An answer of 3 is neutral)', choices=[('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5')], validators=[DataRequired()])
    learning_4 = RadioField('I would be able to repeat the labs without help. (An answer of 3 is neutral)', choices=[('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5')], validators=[DataRequired()])
    learning_5 = TextAreaField('What was your favorite aspect of the lab?', render_kw={'rows':3,'cols':80}, validators=[DataRequired()])
    learning_6 = TextAreaField('What was your favorite aspect of the lab?', render_kw={'rows':3,'cols':80}, validators=[DataRequired()])
    lab_1 = RadioField('The lab instructor was supportive. (An answer of 3 is neutral)', choices=[('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5')], validators=[DataRequired()])
    lab_2 = RadioField('The lab instructor was approachable. (An answer of 3 is neutral)', choices=[('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5')], validators=[DataRequired()])
    lab_3 = RadioField('The lab instructor was able to answer my questions. (An answer of 3 is neutral)', choices=[('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5')], validators=[DataRequired()])
    lab_4 = RadioField('The lab instructor helped me reach a clear understanding of key concepts. (An answer of 3 is neutral)', choices=[('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5')], validators=[DataRequired()])
    lab_5 = RadioField('The lab instructor fostered a mutually respectful learning environment. (An answer of 3 is neutral)', choices=[('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5')], validators=[DataRequired()])
    lab_6 = TextAreaField('What, if anything, could the lab instructor do to improve the experience?', render_kw={'rows':3,'cols':80}, validators=[DataRequired()])
    spaceequipment_1 = RadioField('The amount of lab equipment was sufficient. (An answer of 3 is neutral)', choices=[('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5')], validators=[DataRequired()])
    spaceequipment_2 = RadioField('The available space was sufficient for the lab activities. (An answer of 3 is neutral)', choices=[('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5')], validators=[DataRequired()])
    spaceequipment_3 = RadioField('If lab equipment or setups were not functioning properly, adequate support was available to rectify the situation. (An answer of 3 is neutral)', choices=[('1','1'), ('2','2'), ('3','3'), ('4','4'), ('5','5')], validators=[DataRequired()])
    spaceequipment_4 = TextAreaField('What, if anything, could improve lab space and equipment?', render_kw={'rows':3,'cols':80}, validators=[DataRequired()])
    time_1 = RadioField('On average, the approximate number of hours completing a lab was', choices=[('<2','<2'), ('2','2'), ('2.5','2.5'), ('3','3'), ('>3','>3')], validators=[DataRequired()])
    time_2 = RadioField('How many hours did you spend preparing for the lab?', choices=[('<2','<2'), ('2','2'), ('2.5','2.5'), ('3','3'), ('>3','>3')], validators=[DataRequired()])
    time_3 = RadioField('How many hours did you spend writing lab reports outside the designated lab period?', choices=[('<2','<2'), ('2','2'), ('2.5','2.5'), ('3','3'), ('>3','>3')], validators=[DataRequired()])
    lecture_1 = TextAreaField('What feedback would you give the lecture section instructor (not the lab TA) about the labs?', render_kw={'rows':3,'cols':80}, validators=[DataRequired()])

    submit = SubmitField('Submit')

    # Flask custom validators run when form.validate_on_submit() is called in routes.py,
    # but this requires validate_<attribute>(self, <attribute>) format
    # so this is just a small hack to integrate short custom validators
    def validate_course_id(self, course_id):
        if not studentExists(self.student_id.data, self.course_id.data):
            raise ValidationError('Matching student ID and lab course number not found on roster, please try again.')
