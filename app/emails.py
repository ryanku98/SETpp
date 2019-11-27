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
from threading import get_ident

# TODO: update professors emailing logic, this should be removed after done
def send_email(app, msg_MIME):
    """This is the generic SMTP emailing method that accepts a MIMEMultipart message object"""
    with app.app_context():
        msg_MIME['From'] = current_app.config['MAIL_ADDRESS']
        with smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
            server.starttls(context=ssl.create_default_context())  # Start encrypting traffic
            server.login(current_app.config['MAIL_ADDRESS'], current_app.config['MAIL_PASSWORD'])
            try:
                server.sendmail(current_app.config['MAIL_ADDRESS'], msg_MIME['To'], msg_MIME.as_string())
            except Exception as e:
                print('ERROR: Email to {} failed - {}'.format(msg_MIME['To'], e))

# must pass in student_section_subject and student_section_course_num because they can't be queried (i.e. student.section.subject) outside original app context?
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
            html_body = render_template(os.path.join('email', 'student.html'), student=student, link=link, deadline=deadline)
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
    return (student.email, msg.as_string())

def send_async_emails(app, msg=None, msgs=None):
    """
    If 'msgs' list is not None, sends emails in 'msgs' list of msg_tuples
    If 'msg' tuple is not None, sends email for msg
    This additional list implementation is done to multithread email sending in send_all_student_emails() and send_all_prof_emails() but (hopefully) not reach max connection limit
    """
    with app.app_context(), smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
        sender = current_app.config['MAIL_ADDRESS']
        server.starttls(context=ssl.create_default_context())  # Start encrypting traffic
        server.login(current_app.config['MAIL_ADDRESS'], current_app.config['MAIL_PASSWORD'])
        print(log_header('STUDENT EMAILS'))

        if msgs is not None:
            for msg_tuple in msgs:
                try:
                    server.sendmail(sender, msg_tuple[0], msg_tuple[1])
                    # print('EMAIL {}'.format(msg_tuple[0]))
                    print('EMAIL {} IN THREAD {}'.format(msg_tuple[0], get_ident()))
                except Exception as e:
                    print('ERROR: Email to {} failed - {}'.format(msg_tuple[0], e))
        if msg is not None:
            try:
                server.sendmail(sender, msg[0], msg[1])
                print('EMAIL {}'.format(msg[0]))
            except Exception as e:
                print('ERROR: Email to {} failed - {}'.format(msg[0], e))

def send_all_student_emails(reminder=False):
    """This function sends emails with individualized links to *all* students in the database to take the survey"""
    sender = current_app.config['MAIL_ADDRESS']
    deadline = Deadline.query.first()
    if deadline is not None and deadline.is_valid():
        # msg_queue = queue.Queue()
        msgs = list()
        threads = list()
        current_app_context = current_app._get_current_object()
        for student in Student.query.all():
            if reminder and student.survey_submitted:
                # skip this student if this is a reminder email and the student has already submitted their survey
                continue
            try:
                # get_survey_link() has to be done here because request context cannot be pushed
                # t = Thread(target=lambda q, app_con, sen, stu, sub, num, lin, dea, rem: \
                #     q.put(create_student_msg(app_con, sen, stu, sub, num, lin, dea, rem)), \
                #     args=(msg_queue, current_app._get_current_object(), sender, student, \
                #         student.section.subject, student.section.course_num, student.get_survey_link(), deadline, reminder))
                t = Thread(target=lambda m, app_con, sen, stu, sub, num, lin, dea, rem: \
                    m.insert(0, create_student_msg(app_con, sen, stu, sub, num, lin, dea, rem)), \
                    args=(msgs, current_app_context, sender, student, \
                        student.section.subject, student.section.course_num, student.get_survey_link(), deadline, reminder))
                threads.append(t)
                t.start()
            except Exception as e:
                print('ERROR: Email to {} failed - {}'.format(student.email, e))
        # block until all threads have finished
        for t in threads:
            t.join()

        SPLIT_EVERY_N_MSGS = 2 # value is the size of groups that the messages should be divided up into - increase if max TCP connection limit is still reached
        count = 0
        print(log_header('STUDENT EMAILS'))
        # split msgs into groups of size SPLIT_EVERY_N_MSGS for partial multithreading
        while count < len(msgs):
            # Thread(target=send_async_emails, kwargs={'msgs': msgs[count : count+SPLIT_EVERY_N_MSGS]}).start()
            t = Thread(target=send_async_emails, args=(current_app_context,), kwargs={'msgs': msgs[count : count+SPLIT_EVERY_N_MSGS]})
            t.start()
            print('CREATED THREAD {}'.format(t.ident))
            count += SPLIT_EVERY_N_MSGS

    elif deadline is None:
        print('ERROR: Student emails cannot be sent without a deadline')
    elif not deadline.is_valid():
        print('ERROR: Student emails cannot be sent without a valid deadline')

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
        fname = '{}{}_{}.pdf'.format(section.subject, section.course_num, section.course_id)
        p.add_header(
            'Content-Disposition',
            f'attachment; filename={fname}',
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
    msg['From'] = current_app.config['MAIL_ADDRESS']
    msg['To'] = user.email
    msg['Subject'] = 'Password Reset Request'
    text_body = render_template(os.path.join('email', 'resetPassword.txt'), user=user)
    html_body = render_template(os.path.join('email', 'resetPassword.html'), user=user)
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    try:
        Thread(target=send_async_emails, args=(current_app_context,), kwargs={'msg': (msg['To'], msg.as_string())}).start()
        print('EMAIL (Password Reset): {}'.format(user))
    except: # applies better error handling and avoids issue of both EMAIL log and EMAIL ERROR log printing
        pass
