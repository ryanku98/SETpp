import os
import csv
import smtplib
import email
import ssl
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import url_for

SENDER_EMAIL = "setsystempp@gmail.com"
SENDER_PSWD = "setpp_coen174"
roster = os.path.join('..', 'documents', 'roster.csv')
roster_headers = ['Term', 'Class Nbr', 'Subject', 'Catalog', 'Title', 'Section', 'Instructor', 'Instructor Email', 'Student ID', 'Student', 'Email', 'Tot Enrl', 'Unit Taken', 'Grade', 'Campus', 'Location', 'Add Dt', 'Drop Dt', 'Comb Sect', 'Career', 'Component', 'Session', 'Class Type', 'Grade Base']
student_id_i = 8
course_id_i = 1
instructor_email_i = 7
student_email_i = 9


class Student:
  def __init__(self, name, email, course):
    self.name = name
    self.email = email
    self.course = course


def make_students(roster_file):
    students = []
    with open(roster_file, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            name = row[student_id_i]
            email = row[student_email_i]
            course = row[course_id_i]
            student = Student(name, email, course)
            students.append(student)
    return students


def student_message(student):
    body = "Hello " + student.name + ",\nPlease fill your lab evaluations for course #" + student.course + " out at the following link: google.com"
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = str(student.email)
    message["Subject"] = student.name + ", please fill out your lab evaluations"
    message.attach(MIMEText(body, "plain"))
    msg = message.as_string()
    return msg

# def reset_message():
#     body =

def send_student_email(student):
    msg = student_message(student)
    send_email(student.email, msg)


def send_email(email, msg):           # GENERIC SEND EMAIL
    smtp_server = "smtp.gmail.com"
    port = 587
    context = ssl.create_default_context()
    with smtplib.SMTP(smtp_server, port) as smtp:  #Opens connection with variable name "server"
        smtp.ehlo()   #Identifies with mail server we are using
        smtp.starttls(context=context)   #Start encrypting traffic
        smtp.ehlo()
        smtp.login(SENDER_EMAIL, SENDER_PSWD)
        smtp.sendmail(SENDER_EMAIL, email, msg)

def send_password_reset_email(user):
    token = user.get_reset_password_token()     #generate token for email
    body = "Hello, please follow the link to reset password: " + url_for('resetPassword', token=token, _external=True)
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = "eejohnson@scu.edu"
    message["Subject"] = "Password Reset Request"
    message.attach(MIMEText(body, "plain"))
    msg = message.as_string()
    send_email('eejohnson@scu.edu', msg)



def send_all_student_emails():
    students = make_students(roster)
    for student in students[1:]:
        print(student.name)
        print(student.email)
        print(student.course)
        send_student_email(student)


########
# MAIN #
# send_all_student_emails()



# prof emails (only used at end of deadline)
def make_prof_message(sender_email, student_email, name, courseid):
    body = "Hello " + name + ",\nHere are you TA's teaching results"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = student_email
    message["Subject"] = name + ", please fill out your lab evaluations"
    message.attach(MIMEText(body, "plain"))
    msg = message.as_string()

    return msg


# Runs through roster, checks if student of matching student ID and course ID exists
def studentExists(s_id, c_id):
    with open(roster_file, 'r', newline='') as f_roster:
        csv_roster = csv.reader(f_roster, delimiter=',')
        for row in csv_roster:
            if row[student_id_i] == str(s_id) and row[course_id_i] == str(c_id):
                print('Student found')
                return True
    print('Student not found')
    return False
