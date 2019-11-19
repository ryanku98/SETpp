import os
import smtplib
import ssl
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from flask import render_template, current_app
from app.models import Section, Student, Result, Deadline, log_header
from app.plot import PDFPlotter
import queue
from threading import Thread

# def send_email(app, msg_MIME):
#     """This is the generic SMTP emailing method that accepts a MIMEMultipart message object"""
#     with app.app_context():
#         msg_MIME['From'] = current_app.config['MAIL_ADDRESS']
#         with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
#             server.starttls(context=ssl.create_default_context())  # Start encrypting traffic
#             server.login(current_app.config['MAIL_ADDRESS'], current_app.config['MAIL_PASSWORD'])
#             try:
#                 server.sendmail(current_app.config['MAIL_ADDRESS'], msg_MIME['To'], msg_MIME.as_string())
#             except Exception as e:
#                 print('ERROR: Email to {} failed - {}'.format(msg_MIME['To'], e))

# def send_student_msg(student, reminder=False):
#     """This function creates and sends a personalized email to the student represented by the student object passed in"""
#     msg = MIMEMultipart('alternative')
#     msg['To'] = student.email
#     msg['Subject'] = 'Fill Out Your SET++ Lab Evaluations for {}{} - Section {}'.format(student.section.subject, student.section.course_num, student.section.course_id)
#     if reminder:
#         # add REMINDER to subject line if is reminder
#         msg['Subject'] = 'REMINDER: ' + msg['Subject']
#     deadline = Deadline.query.first()
#     if deadline is not None and deadline.is_valid():
#         text_body = render_template(os.path.join('email', 'student.txt'), student=student, deadline=deadline)
#         html_body = render_template(os.path.join('email', 'student.html'), student=student, deadline=deadline)
#         msg.attach(MIMEText(text_body, 'plain'))
#         msg.attach(MIMEText(html_body, 'html'))
#         try:
#             Thread(target=send_email, args=(current_app._get_current_object(), msg)).start()
#             print('EMAIL: {}'.format(student))
#         except: # applies better error handling and avoids issue of both EMAIL log and EMAIL ERROR log printing
#             pass
#     elif deadline is None:
#         print('ERROR: Student emails cannot be sent without a deadline')
#     elif not deadline.is_valid():
#         print('ERROR: Student emails cannot be sent without a valid deadline')

# cannot pass in a student object because this is a new thread and SQLite errors out when querying it (i.e.student.section)
# def create_student_msg(sender, student, deadline, reminder=False):
def create_student_msg(app, sender, student, student_section_subject, student_section_course_num, link, deadline, reminder=False):
    msg = MIMEMultipart('alternative')
    msg['From'] = sender
    msg['To'] = student.email
    msg['Subject'] = 'Fill Out Your SET++ Lab Evaluations for {}{} - Section {}'.format(student_section_subject, student_section_course_num, student.c_id)
    if reminder:
        # add REMINDER to subject line if is reminder
        msg['Subject'] = 'REMINDER: ' + msg['Subject']
    if deadline is not None and deadline.is_valid():
        with app.app_context():
            text_body = render_template(os.path.join('email', 'student.txt'), student=student, link=link, deadline=deadline)
            html_body = render_template(os.path.join('email', 'student.html'), student=student, deadline=deadline)
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
    return (student.email, msg.as_string())

# def test_sender(server, sender, email, msg):
#     print('flag1')
#     try:
#         server.sendmail(sender, email, msg)
#         print('flag2')
#     except Exception as e:
#         print('OMFG: {}'.format(e))

def send_all_student_emails(reminder=False):
    """This function sends emails with individualized links to *all* students in the database to take the survey"""
    sender = current_app.config['MAIL_ADDRESS']
    deadline = Deadline.query.first()
    if deadline is not None and deadline.is_valid():
        msg_queue = queue.Queue()
        threads = list()
        for student in Student.query.all():
            if reminder and student.survey_submitted:
                # skip this student if this is a reminder email and the student has already submitted their survey
                continue
            try:
                # get_survey_link() has to be done here because request context cannot be push
                t = Thread(target=lambda q, app_con, sen, stu, sub, num, lin, dea, rem: \
                    q.put(create_student_msg(app_con, sen, stu, sub, num, lin, dea, rem)), \
                    args=(msg_queue, current_app._get_current_object(), sender, student, \
                    student.section.subject, student.section.course_num, student.get_survey_link(), deadline, reminder))
                threads.append(t)
                t.start()
            except Exception as e:
                print('ERROR: Email to {} failed - {}'.format(student.email, e))
        # block until all threads have finished
        for t in threads:
            t.join()

        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            server.starttls(context=ssl.create_default_context())  # Start encrypting traffic
            server.login(current_app.config['MAIL_ADDRESS'], current_app.config['MAIL_PASSWORD'])
            print(log_header('STUDENT EMAILS'))
            while not msg_queue.empty():
                msg_tuple = msg_queue.get()
                try:
                    server.sendmail(sender, msg_tuple[0], msg_tuple[1])
                    print('EMAIL {}'.format(msg_tuple[0]))
                except Exception as e:
                    print('ERROR: Email to {} failed - {}'.format(msg_tuple[0], e))

    elif deadline is None:
        print('ERROR: Student emails cannot be sent without a deadline')
    elif not deadline.is_valid():
        print('ERROR: Student emails cannot be sent without a valid deadline')

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
