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
from app.survey import s_id_i_roster, c_id_i_roster, prof_email_i_roster, stud_email_i_roster, roster_file, results_file

# STUDENT CLASS
class Student:
    def __init__(self, id, email, course):
        self.id = id
        self.email = email
        self.course = course

    def create_message(self):
        '''Creates an email message string based on the student'''
        stud_msg_template = os.path.join('app', 'templates', 'email', 'studentSurveyLink.txt')
        with open(stud_msg_template, 'r') as file:
            body = file.read().format(self.id, self.course, LINK)
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = self.email
        message["Subject"] = "{} - {}".format(self.id, SUBJECT)
        message.attach(MIMEText(body, "plain"))
        return message.as_string()

    # Function to call on a student to send an email to the student
    def send_email(self):
        email(self.email, self.create_message())

def send_all_student_emails():
    '''This is the function that should be called when the survey is started'''
    with open(roster_file, newline='') as csvfile:
        next(csvfile)
        sr = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in sr:
            s_id = row[s_id_i_roster]
            email = row[stud_email_i_roster]
            c_id = row[c_id_i_roster]
            if s_id and email and c_id:
                student = Student(s_id, email, c_id)
                student.send_email()
                print("Sent email to student {}".format(email))

# PROFESSOR CLASS
class Professor:
    def __init__(self, email, course):
        self.email = email
        self.course = course

    def create_message(self):
        '''Will be pretty similar to one above, pull from the other email template'''
        prof_msg_template = os.path.join('app', 'templates', 'email', 'professorSurveyStatistics.txt')
        with open(prof_msg_template, 'r') as file:
            body = file.read().format(self.email, LINK)
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = self.email
        message["Subject"] =  "Professor {} - {} - Lab {}".format(self.email, SUBJECT, self.course)
        message.attach(MIMEText(body, "plain"))
        return message.as_string()

    def send_email(self):
        email(self.email, self.create_message())

def send_all_prof_emails():
    '''Function to email all professors'''
    with open(results_file, newline='') as csvfile:
        next(csvfile)
        sr = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in sr:
            email = row[prof_ema]
            c_id = row[course_]
            if row[prof_ema] and row[course_]:
                prof = Professor(email)
                prof.send_email()
                print("Sent email to professor {}".format(email))

def email(email, msg):
    '''This is the generic SMTP emailing method (able to be used anywhere)'''
    SENDER_EMAIL = "setsystempp@gmail.com"; SENDER_PSWD = "setpp_coen174"
    SUBJECT = "SET++ Lab Evaluations"; LINK = "http://localhost:5000/survey"
    smtp_server = "smtp.gmail.com"
    port = 587
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as smtp:   # Opens connection with variable name "server"
        smtp.ehlo() # Identifies with mail server we are using
        smtp.starttls(context=context)  # Start encrypting traffic
        smtp.ehlo()
        smtp.login(SENDER_EMAIL, SENDER_PSWD)
        try:
            smtp.sendmail(SENDER_EMAIL, email, msg)
        except:
            print("Error: invalid email")

# password reset email
def send_password_reset_email(user):
    '''Evan's password reset function'''
    token = user.get_reset_password_token() # generate token for email
    body = "Hello, please follow the link to reset password: " + url_for('resetPassword', token=token, _external=True)
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = user.email
    message["Subject"] = "Password Reset Request"
    message.attach(MIMEText(body, "plain"))
    msg = message.as_string()
    Thread( target = email, args = (message['To'], msg) ).start()
