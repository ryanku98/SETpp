import os
import csv
import smtplib
import ssl
import email
from flask import url_for
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from threading import Thread
from app.survey import student_id_i, course_id_i, prof_email_i, student_email_i, roster_file, results_file

# STUDENT CLASS
class Student:
    def __init__(self, name, email, course):
        self.name = name
        self.email = email
        self.course = course

    def create_message(self):
        '''Creates an email message string based on the student'''
        stud_msg_template = os.path.join('app', 'templates', 'email', 'studentSurveyLink.txt')
        with open(stud_msg_template, 'r') as file:
            body = file.read().format(self.name, self.course, LINK)
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = self.email
        message["Subject"] = "{} - {}".format(self.name, SUBJECT)
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
            if row[student_id_i] and row[student_email_i] and row[course_id_i]:
                student = Student(name, email, course)
                student.send_email()
                print("Sent email to student {}".format(email))

# PROFESSOR CLASS
class Professor:
    def __init__(self, email):
        self.email = email

    def create_message(self):
        '''Will be pretty similar to one above, pull from the other email template'''
        prof_msg_template = os.path.join('app', 'templates', 'email', 'professorSurveyStatistics.txt')
        with open(prof_msg_template, 'r') as file:
            body = file.read().format(self.email, LINK)
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = self.email
        message["Subject"] =  "Professor {} - {}".format(self.email, SUBJECT)
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
            if row[prof_email_i] and row[course_id_i]:
                prof = Professor(name, email, course)
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
