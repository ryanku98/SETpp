import os
import csv
import smtplib
import email
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


SENDER_EMAIL = "setsystempp@gmail.com"; SENDER_PSWD = "setpp_coen174"
SUBJECT = "SET++ Lab Evaluations"; LINK = "google.com"
email_msg = os.path.join('templates', 'email', 'studentSurveyLink.txt')
roster = os.path.join('..', 'documents', 'roster.csv')
roster_headers = ['Term', 'Class Nbr', 'Subject', 'Catalog', 'Title', 'Section', 'Instructor', 'Instructor Email', 'Student ID', 'Student', 'Email', 'Tot Enrl', 'Unit Taken', 'Grade', 'Campus', 'Location', 'Add Dt', 'Drop Dt', 'Comb Sect', 'Career', 'Component', 'Session', 'Class Type', 'Grade Base']
student_id_i = 8
course_id_i = 1
prof_email_i = 7
student_email_i = 9


class Student:
    def __init__(self, name, email, course):
        self.name = name
        self.email = email
        self.course = course

    # Creates an email message string based on the student
    def create_message(self):
        with open(email_msg, 'r') as file:
            body = file.read().format(self.name, self.course, LINK)
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = str(self.email)
        message["Subject"] = "{} {}".format(self.name, SUBJECT)
        message.attach(MIMEText(body, "plain"))
        msg = message.as_string()
        return msg

    # Function to call on a student to send an email to the student
    def send_email(self):
        msg = self.create_message()
        email(self.email, msg)


class Professor:
    def __init__(self, email):
        self.email = email

    def create_message(self):
        body = "Hello " + self.name + ",\nHere are you TA's teaching results"
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = self.email
        message["Subject"] = self.name + ", please fill out your lab evaluations"
        message.attach(MIMEText(body, "plain"))
        msg = message.as_string()
        return msg


# Function to email all professors
# TODO fix this
def get_profs(roster_file):
    profs = []
    with open(roster_file, newline='') as csvfile:
        next(csvfile)
        sr = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in sr:
            email = row[student_email_i]
            course = row[course_id_i]
            prof = Professor(email)
            profs.append(prof)
    return profs


# This is the generic SMTP emailing method (able to be used anywhere)
def email(email, msg):
    smtp_server = "smtp.gmail.com"
    port = 587
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as smtp:  #Opens connection with variable name "server"
        smtp.ehlo()   #Identifies with mail server we are using
        smtp.starttls(context=context)   #Start encrypting traffic
        smtp.ehlo()
        smtp.login(SENDER_EMAIL, SENDER_PSWD)
        smtp.sendmail(SENDER_EMAIL, email, msg)

# This is the function that should be called when the survey is started
def send_all_student_emails():
    with open(roster, newline='') as csvfile:
        next(csvfile)
        sr = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in sr:
            name = row[student_id_i]
            email = row[student_email_i]
            course = row[course_id_i]
            student = Student(name, email, course)
            student.send_email()
            print("sent email to " + email)


# MAIN
send_all_student_emails()


# end
