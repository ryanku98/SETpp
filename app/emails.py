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
from threading import Thread, get_ident

def send_async_emails(app, msg=None, msgs=None):
    """
    Sends an email/list of emails - designed to run on its own thread
    If 'msgs' list is not None, sends emails in 'msgs' list of msg_tuples
    If 'msg' tuple is not None, sends email for msg
    This additional list implementation is done to multithread email sending in send_all_student_emails() and send_all_prof_emails() but (hopefully) not reach max connection limit
    """
    N_MESSAGES_PER_THREAD = 25 # value is the size of groups that the messages should be divided up into - increase if max TCP connection limit is still reached
    with app.app_context(), smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT']) as server:
        sender = current_app.config['MAIL_ADDRESS']
        server.starttls(context=ssl.create_default_context())  # Start encrypting traffic
        server.login(current_app.config['MAIL_ADDRESS'], current_app.config['MAIL_PASSWORD'])
        print('CREATED EMAILING THREAD {}'.format(get_ident()))

        if msgs is not None:
            if len(msgs) > N_MESSAGES_PER_THREAD:
                # start new thread for latter portion if msgs list is longer than N_MESSAGES_PER_THREAD
                Thread(target=send_async_emails, args=(app,), kwargs={'msgs': msgs[N_MESSAGES_PER_THREAD :]}).start()
            for msg_tuple in msgs[: N_MESSAGES_PER_THREAD]:
                try:
                    server.sendmail(sender, msg_tuple[0], msg_tuple[1])
                    print('EMAIL: {} IN THREAD {}'.format(msg_tuple[0], get_ident()))
                except Exception as e:
                    print('ERROR: Email to {} failed - {}'.format(msg_tuple[0], e))
        if msg is not None:
            try:
                server.sendmail(sender, msg[0], msg[1])
                print('EMAIL: {}'.format(msg[0]))
            except Exception as e:
                print('ERROR: Email to {} failed - {}'.format(msg[0], e))

# must pass in student_section_subject and student_section_course_num because they can't be queried (i.e. student.section.subject) outside original app context?
def create_student_msg(app, student, student_section_subject, student_section_course_num, link, deadline, reminder=False):
    """Creates individual email messages personalized for each student - requires many non-SQLite objects because cannot pass in SQLite objects into this method, which is designed to run on a different thread"""
    msg = MIMEMultipart('alternative')
    with app.app_context():
        msg['From'] = current_app.config['MAIL_ADDRESS']
    msg['To'] = student.email
    # msg dict values cannot be rewritten after the first time for some reason, so doing this the static way
    if reminder:
        # add REMINDER to subject line if is reminder
        msg['Subject'] = 'REMINDER: Fill Out Your SET++ Lab Evaluations for {}{} - Section {}'.format(student_section_subject, student_section_course_num, student.c_id)
    else:
        msg['Subject'] = 'Fill Out Your SET++ Lab Evaluations for {}{} - Section {}'.format(student_section_subject, student_section_course_num, student.c_id)
    if deadline is not None and deadline.is_valid():
        with app.app_context():
            text_body = render_template(os.path.join('email', 'student.txt'), student=student, link=link, deadline=deadline)
            html_body = render_template(os.path.join('email', 'student.html'), student=student, link=link, deadline=deadline)
        msg.attach(MIMEText(text_body, 'plain'))
        msg.attach(MIMEText(html_body, 'html'))
    return (student.email, msg.as_string())

def send_all_student_emails(reminder=False):
    """This function sends emails with individualized links to *all* students in the database to take the survey"""
    sender = current_app.config['MAIL_ADDRESS']
    deadline = Deadline.query.first()
    if deadline is not None and deadline.is_valid():
        msgs = list()
        threads = list()
        current_app_context = current_app._get_current_object()
        for student in Student.query.all():
            # skip this student if this is a reminder email and the student has already submitted their survey
            if not reminder or not student.survey_submitted:
                try:
                    # get_survey_link() has to be done here because request context cannot be pushed
                    t = Thread(target=lambda m, app_con, stu, sub, num, lin, dea, rem: \
                        m.insert(0, create_student_msg(app_con, stu, sub, num, lin, dea, rem)), \
                        args=(msgs, current_app_context, student, student.section.subject, \
                            student.section.course_num, student.get_survey_link(), deadline, reminder))
                    threads.append(t)
                    t.start()
                except Exception as e:
                    print('ERROR: Failed to create message for {} {} - {}'.format(student.s_id, student.email, e))
        # block until all threads have finished
        for t in threads:
            t.join()
        # send emails
        if reminder:
            print(log_header('REMINDER EMAILS'))
        else:
            print(log_header('STUDENT EMAILS'))
        Thread(target=send_async_emails, args=(current_app_context,), kwargs={'msgs': msgs}).start()
        print('SENT {} EMAILS'.format(len(msgs)))
    elif deadline is None:
        print('ERROR: Student emails cannot be sent without a deadline')
    elif not deadline.is_valid():
        print('ERROR: Student emails cannot be sent without a valid deadline')

# must pass in results_count and students_count because they can't be queried in a different thread
def create_prof_emails(app, section, results_count, students_count, means, stds, frq_responses, file=None):
    """Creates personalized statistics for emails for each individual lab section - requires many non-SQLite objects because cannot pass in SQLite objects into this method, which is designed to run on a different thread"""
    msg = MIMEMultipart('alternative')
    with app.app_context():
        msg['From'] = current_app.config['MAIL_ADDRESS']
    msg['To'] = section.prof_email
    msg['Subject'] = 'SET++ Lab Evaluations Statistics for {}{} - Section {}'.format(section.subject, section.course_num, section.course_id)
    with app.app_context():
        # must pass in enumerate function because Jinja doesn't recognize it
        text_body = render_template(os.path.join('email', 'professor.txt'), section=section, results_count=results_count, students_count=students_count, means=means, stds=stds, frq_responses=frq_responses, enumerate=enumerate)
        html_body = render_template(os.path.join('email', 'professor.html'), section=section, results_count=results_count, students_count=students_count, means=means, stds=stds, frq_responses=frq_responses, enumerate=enumerate)
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))

    # only attempt to open if one was created (at least 1 result was submitted)
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
    return (section.prof_email, msg.as_string())

def send_all_prof_emails():
    """This function sends emails with individualized statistics to *all* professors in the database (represented as sections)"""
    current_app_context = current_app._get_current_object()
    msgs = list()
    threads = list()
    pdfs = list()
    for section in Section.query.all():
        t = None
        # create section data
        results_count = section.results.count()
        students_count = section.students.count()
        means = section.get_means()
        stds = section.get_stds()
        frq_responses = section.get_frq_responses()
        try:
            if results_count > 0:
                pdf = PDFPlotter(section)
                t = Thread(target=lambda m, app_con, s, r_c, s_c, me, st, f_r, f: \
                    m.insert(0, create_prof_emails(app_con, s, r_c, s_c, me, st, f_r, f)), \
                    args=(msgs, current_app_context, section, results_count, students_count, means, stds, frq_responses, pdf.file))
                pdfs.append(pdf)
            else:
                # don't create PDF if no results were submitted
                t = Thread(target=lambda m, app_con, s, r_c, s_c, me, st, f_r: \
                    m.insert(0, create_prof_emails(app_con, s, r_c, s_c, me, st, f_r)), \
                    args=(msgs, current_app_context, section, results_count, students_count, means, stds, frq_responses))
            threads.append(t)
            t.start()
        except Exception as e:
            print('ERROR: Failed to create message for {} {} - {}'.format(section.course_id, section.prof_email, e))
    # block until all threads are finished
    for t in threads:
        t.join()
    # delete pdfs after emails are sent
    for pdf in pdfs:
        pdf.deleteFile()
    # send emails
    print(log_header('PROFESSOR EMAILS'))
    Thread(target=send_async_emails, args=(current_app_context,), kwargs={'msgs': msgs}).start()
    print('SENT {} EMAILS'.format(len(msgs)))

def send_password_reset_email(user):
    """Sends a reset password email with a generated JWT token"""
    msg = MIMEMultipart('alternative')
    msg['From'] = current_app.config['MAIL_ADDRESS']
    msg['To'] = user.email
    msg['Subject'] = 'Password Reset Request'
    text_body = render_template(os.path.join('email', 'resetPassword.txt'), user=user)
    html_body = render_template(os.path.join('email', 'resetPassword.html'), user=user)
    msg.attach(MIMEText(text_body, 'plain'))
    msg.attach(MIMEText(html_body, 'html'))
    try:
        Thread(target=send_async_emails, args=(current_app._get_current_object(),), kwargs={'msg': (msg['To'], msg.as_string())}).start()
        print('EMAIL (Password Reset): {}'.format(user))
    except Exception as e:
        print('ERROR: Password reset email to {} failed: {}'.format(user.email, e))
