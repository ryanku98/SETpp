from app import app
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, SurveyForm

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for admin {}, remember_me={}'.format(form.username.data, form.remember_me.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
    
@app.route('/survey', methods=['GET', 'POST'])
def survey():
    form = SurveyForm()
    if form.validate_on_submit():
        flash('Survey submission requested for student {}, course {}'.format(form.student_id.data, form.course_id.data))
        return redirect(url_for('survey'))
    return render_template('survey.html', form=form)