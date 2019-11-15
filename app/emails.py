import os
import smtplib
import ssl
import email
import pandas as pd
from email import encoders
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import url_for, render_template
from threading import Thread
from app import app
from app.models import Section, Student, Result, Deadline, log_header

def send_email(msg_MIME):
    """This is the generic SMTP emailing method that accepts a MIMEMultipart message object"""
    msg_MIME['From'] = app.config['ADMIN']
    with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
        server.starttls(context=ssl.create_default_context())  # Start encrypting traffic
        server.login(app.config['ADMIN'], app.config['MAIL_PASSWORD'])
        try:
            server.sendmail(app.config['ADMIN'], msg_MIME['To'], msg_MIME.as_string())
        except:
            print('ERROR: Email to {} failed'.format(msg_MIME['To']))

def send_student_msg(student, msg):
    """This function creates and sends a personalized email to the student represented by the student object passed in"""
    msg = MIMEMultipart('alternative')
    msg['To'] = student.email
    msg['Subject'] = 'Fill Out Your SET++ Lab Evaluations for {}{} - Section {}'.format(student.section.subject, student.section.course_num, student.section.course_id)
    deadline = Deadline.query.first()
    text_body = render_template(os.path.join('email', 'student.txt'), student=student, deadline=deadline)
    html_body = render_template(os.path.join('email', 'student.html'), student=student, deadline=deadline)
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    try:
        Thread(target=send_email, args=(msg,)).start()
        print('EMAIL: {}'.format(student))
    except: # applies better error handling and avoids issue of both EMAIL log and EMAIL ERROR log printing
        pass

def send_all_student_emails():
    """This function sends emails with individualized links to *all* students in the database to take the survey"""
    print(log_header('STUDENT EMAILS'))
    for student in Student.query.all():
        send_student_msg(student)

def send_reminder_msg(student):
    pass

def send_all_reminder_emails():
    pass

def send_prof_msg(section):
    """This function creates and sends a personalized statistics email to the professor represented by the section object passed in"""
    msg = MIMEMultipart('alternative')
    msg['To'] = section.prof_email
    msg['Subject'] = 'SET++ Lab Evaluations Statistics for {}{} - Section {}'.format(section.subject, section.course_num, section.course_id)
    text_body = render_template(os.path.join('email', 'professor.txt'), section=section, enumerate=enumerate)
    html_body = render_template(os.path.join('email', 'professor.html'), section=section, enumerate=enumerate)
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    try:
        Thread(target=send_email, args=(msg,)).start()
        print('EMAIL: <Professor {} - Email {}>'.format(section.prof_name, section.prof_email))
    except: # applies better error handling and avoids issue of both EMAIL log and EMAIL ERROR log printing
        pass

def send_all_prof_emails():
    """This function sends emails with individualized statistics to *all* professors in the database (represented as sections)"""
    print(log_header('PROFESSOR EMAILS'))
    for section in Section.query.all():
        send_prof_msg(section)

# password reset email
def send_password_reset_email(user):
    """Function called to send an email with reset password link"""
    msg = MIMEMultipart('alternative')
    msg['To'] = user.email
    msg['Subject'] = 'Password Reset Request'
    text_body = render_template(os.path.join('email', 'resetPassword.txt'), user=user)
    html_body = render_template(os.path.join('email', 'resetPassword.html'), user=user)
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    try:
        Thread(target=send_email, args=(msg,)).start()
        print('EMAIL (Password Reset): {}'.format(user))
    except: # applies better error handling and avoids issue of both EMAIL log and EMAIL ERROR log printing
        pass

