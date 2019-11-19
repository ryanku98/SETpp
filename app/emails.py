import os
import smtplib
import ssl
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import render_template, current_app
from threading import Thread
# from app import app
from app.models import Section, Student, Result, Deadline, log_header
from app.plot import PDFPlotter

def send_email(app, msg_MIME):
    """This is the generic SMTP emailing method that accepts a MIMEMultipart message object"""
    with app.app_context():
        msg_MIME['From'] = current_app.config['MAIL_ADDRESS']
        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            server.starttls(context=ssl.create_default_context())  # Start encrypting traffic
            server.login(current_app.config['MAIL_ADDRESS'], current_app.config['MAIL_PASSWORD'])
            try:
                server.sendmail(current_app.config['MAIL_ADDRESS'], msg_MIME['To'], msg_MIME.as_string())
            except:
                print('ERROR: Email to {} failed'.format(msg_MIME['To']))

def send_student_msg(student, reminder=False):
    """This function creates and sends a personalized email to the student represented by the student object passed in"""
    msg = MIMEMultipart('alternative')
    msg['To'] = student.email
    msg['Subject'] = 'Fill Out Your SET++ Lab Evaluations for {}{} - Section {}'.format(student.section.subject, student.section.course_num, student.section.course_id)
    if reminder:
        # add REMINDER to subject line if is reminder
        msg['Subject'] = 'REMINDER: ' + msg['Subject']
    deadline = Deadline.query.first()
    if deadline is not None and deadline.is_valid():
        text_body = render_template(os.path.join('email', 'student.txt'), student=student, deadline=deadline)
        html_body = render_template(os.path.join('email', 'student.html'), student=student, deadline=deadline)
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
        try:
            Thread(target=send_email, args=(current_app._get_current_object(), msg)).start()
            print('EMAIL: {}'.format(student))
        except: # applies better error handling and avoids issue of both EMAIL log and EMAIL ERROR log printing
            pass
    elif deadline is None:
        print('ERROR: Student emails cannot be sent without a deadline')
    elif not deadline.is_valid():
        print('ERROR: Student emails cannot be sent without a valid deadline')

def send_all_student_emails():
    """This function sends emails with individualized links to *all* students in the database to take the survey"""
    print(log_header('STUDENT EMAILS'))
    for student in Student.query.all():
        # cannot multithread here because it breaks some Jinja2 context that breaks render_template() inside the thread for some reason
        send_student_msg(student)

def send_all_reminder_emails():
    """This function sends email reminders with individualized links to all students in the database that haven't submitted a survey yet"""
    print(log_header('STUDENT REMINDER EMAILS'))
    for student in Student.query.all():
        if not student.survey_submitted:
            # cannot multithread here because it breaks some Jinja2 context that breaks render_template() inside the thread for some reason
            send_student_msg(student, True)

def send_prof_msg(section, file=None):
    """This function creates and sends a personalized statistics email to the professor represented by the section object passed in"""
    msg = MIMEMultipart('alternative')
    msg['To'] = section.prof_email
    msg['Subject'] = 'SET++ Lab Evaluations Statistics for {}{} - Section {}'.format(section.subject, section.course_num, section.course_id)
    # must pass in enumerate function because Jinja doesn't recognize it
    text_body = render_template(os.path.join('email', 'professor.txt'), section=section, enumerate=enumerate)
    html_body = render_template(os.path.join('email', 'professor.html'), section=section, enumerate=enumerate)
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    # only attmpt to open if one was created (at least 1 result was submitted)
    if file is not None:
        # create PDF attachment
        with open(file, 'rb') as attachment:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload((attachment).read())
        encoders.encode_base64(p) # encode binary data into base64 - printable ASCII characters
        p.add_header(
            'Content-Disposition',
            f'attachment; filename= {file}',
        )
        msg.attach(p)

    try:
        Thread(target=send_email, args=(current_app._get_current_object(), msg)).start()
        print('EMAIL: <Professor {} - Email {}>'.format(section.prof_name, section.prof_email))
    except: # applies better error handling and avoids issue of both EMAIL log and EMAIL ERROR log printing
        pass

def send_all_prof_emails():
    """This function sends emails with individualized statistics to *all* professors in the database (represented as sections)"""
    print(log_header('PROFESSOR EMAILS'))
    for section in Section.query.all():
        if section.results.count() > 0:
            pdf = PDFPlotter(section)
            pdf.createPDF()
            # cannot multithread here because it breaks some Jinja2 context that breaks render_template() inside the thread for some reason
            send_prof_msg(section, pdf.file)
            pdf.deleteFile()
        else:
            # don't create PDF if no results were submitted
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
