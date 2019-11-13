import os
import csv
import smtplib
import ssl
import email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import url_for
from threading import Thread
from app.survey import s_id_i_roster, c_id_i_roster, prof_email_i_roster, fr_ids, stud_email_i_roster, prof_email_i_results, c_id_i_results, roster_file, results_file, getSortedResults, getResultsHeaders, studentExists, removeZeroes, Section

SENDER_EMAIL = "setsystempp@gmail.com"
SURVEY_LINK = "http://localhost:5000/survey"
SUBJECT = "SET++ Lab Evaluations"

def send_email(email, msg):
    """This is the generic SMTP emailing method (able to be used anywhere)"""
    SENDER_PSWD = "setpp_coen174"
    smtp_server = "smtp.gmail.com"
    port = 587
    context = ssl.create_default_context()
    print("Sending email to "+str(email))
    with smtplib.SMTP(smtp_server, port) as smtp:   # Opens connection with variable name "server"
        smtp.ehlo() # Identifies with mail server we are using
        smtp.starttls(context=context)  # Start encrypting traffic
        smtp.ehlo()
        smtp.login(SENDER_EMAIL, SENDER_PSWD)
        try:
            smtp.sendmail(SENDER_EMAIL, email, msg)
        except:
            print("Error: invalid email")

# STUDENT CLASS
class Student:
    def __init__(self, id, email, course):
        self.id = id
        self.email = email
        self.course = course

    def create_message(self):
        """Creates an email message string based on the student"""
        stud_msg_template = os.path.join('app', 'templates', 'email', 'studentSurveyLink.txt')
        with open(stud_msg_template, 'r') as file:
            link = SURVEY_LINK
            # create query string values for form prefilling
            if studentExists(self.id, self.course):
                link = SURVEY_LINK + '?s=' + self.id + '&c=' + self.course
            body = file.read().format(self.id, self.course, link)
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = self.email
        message["Subject"] = "{} - {}".format(self.id, SUBJECT)
        message.attach(MIMEText(body, "plain"))
        return message.as_string()

    # Function to call on a student to send an email to the student
    def send_message(self):
        Thread( target = send_email, args = (self.email, self.create_message()) ).start()

def send_all_student_emails():
    """This is the function that should be called when the survey is started"""
    with open(roster_file, newline='') as csvfile:
        next(csvfile)
        sr = csv.reader(csvfile, delimiter=',')
        for row in sr:
            s_id = removeZeroes(row[s_id_i_roster])
            email = row[stud_email_i_roster]
            c_id = removeZeroes(row[c_id_i_roster])
            if s_id and email and c_id:
                student = Student(s_id, email, c_id)
                student.send_message()
                print("Sent email to student {}".format(email))

# PROFESSOR CLASS
class Professor:
    def __init__(self, email, section): # email, course id, Section class
        self.email = email
        self.section = section

    def create_message(self):
        """Will be pretty similar to one above, pull from the other email template"""
        prof_msg_template = os.path.join('app', 'templates', 'email', 'professorSurveyStatistics.txt')
        with open(prof_msg_template, 'r') as file:
            # stats = format_stats(self.email, self.section.course_id, self.section.mean_list, self.section.std_list, self.section.fr_list)
            stats = self.section.format_stats(self.email)
            body = file.read().format(*stats)

        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = self.email
        message["Subject"] =  "Professor {} - {} - Lab {}".format(self.email, SUBJECT, self.section.course_id)
        message.attach(MIMEText(body, "plain"))
        return message.as_string()

    def send_message(self):
        Thread( target = send_email, args = (self.email, self.create_message()) ).start()
        # send_email(self.email, self.create_message())
        # print('Sending email to {} for section {}'.format(self.email, self.section.course_id))

def send_all_prof_emails():
    """Function to email all professors"""
    # print(getResultsHeaders())
    df = getSortedResults()
    prev_id = -1
    prev_index = 0
    for index, row in enumerate(df):
        # if found end of new section
        curr_id = row[c_id_i_results]
        if curr_id != prev_id and index != prev_index:
            prof = Professor(email=df[prev_index][prof_email_i_results], section=Section(df[prev_index][c_id_i_results], df[prev_index:index]))
            prof.send_message()
            prev_index = index
        prev_id = row[c_id_i_results]
    # send result of last section
    prof = Professor(email=df[prev_index][prof_email_i_results], section=Section(df[prev_index][c_id_i_results], df[prev_index:len(df)]))
    prof.send_message()

# password reset email
def send_password_reset_email(user):
    """Function called to send an email with reset password link"""
    token = user.get_reset_password_token() # generate token for email
    body = "Hello, please follow the link to reset password: " + url_for('resetPassword', token=token, _external=True)
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = user.email
    message["Subject"] = "Password Reset Request"
    message.attach(MIMEText(body, "plain"))
    msg = message.as_string()
    Thread( target = send_email, args = (message['To'], msg) ).start()

# send_all_prof_emails()
