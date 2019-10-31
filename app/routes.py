from app import app, db
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm, SurveyForm
from flask_login import current_user, login_user, login_required
from app.models import User

@app.route('/')
@app.route('/index')
# @login_required
def index():
    if not current_user.is_authenticated:
        flash('Login to view admin page!')
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # @EVAN put login stuff here
        flash('Login requested for admin {}, remember_me={}'.format(form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if User.query.count() != 0:
        flash('Redirected to login page: An admin already exists for this system. Please login for admin privileges.')
        return redirect(url_for('login'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congrats, you are now an admin!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
    
@app.route('/survey', methods=['GET', 'POST'])
def survey():
    form = SurveyForm()
    if form.validate_on_submit():
        flash('Survey submission requested for student {}, course {}'.format(form.student_id.data, form.course_id.data))
        return redirect(url_for('survey'))
    return render_template('survey.html', form=form)