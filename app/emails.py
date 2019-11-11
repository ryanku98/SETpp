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
from survey import s_id_i_roster, c_id_i_roster, prof_email_i_roster, stud_email_i_roster, prof_email_i_results, c_id_i_results, roster_file, results_file, studentExists, removeZeroes, Section

SENDER_EMAIL = "setsystempp@gmail.com"
SURVEY_LINK = "http://localhost:5000/survey"
SUBJECT = "SET++ Lab Evaluations"

def send_email(email, msg):
    """This is the generic SMTP emailing method (able to be used anywhere)"""
    SENDER_PSWD = "setpp_coen174"
    smtp_server = "smtp.gmail.com"
    port = 587
    context = ssl.create_default_context()
    print("Sending mail to "+str(email))
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
        send_email(self.email, self.create_message())

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
    def __init__(self, email, course, section):
        self.email = email
        self.course = course
        self.section = section

    def create_message(self):
        """Will be pretty similar to one above, pull from the other email template"""
        prof_msg_template = os.path.join('app', 'templates', 'email', 'professorSurveyStatistics.txt')
        with open(prof_msg_template, 'r') as file:
            body = file.read().format(self.email, self.section.mean_list, self.section.std_list, self.section.fr_list)
        message = MIMEMultipart()
        message["From"] = SENDER_EMAIL
        message["To"] = self.email
        message["Subject"] =  "Professor {} - {} - Lab {}".format(self.email, SUBJECT, self.course)
        message.attach(MIMEText(body, "plain"))
        return message.as_string()

    def send_message(self):
        Thread( target = send_email, args = (self.email, self.create_message()) ).start()

def send_all_prof_emails():
    '''Function to email all professors'''
    with open(results_file, newline='') as csvfile:
        for i in range(20):
            next(csvfile)
        sr = csv.reader(csvfile, delimiter=',', quotechar='|')
        df = []
        for row in sr:
            df.append(row)
        df = sorted(df, key=lambda x: x[1])
        print(df)
        prev_id = -1
        prev_index = 0
        for index,row in enumerate(df):
            if row[1] != prev_id and len(df[prev_index:index]) != 0:
                email_addr = df[prev_index][0]
                course_id = df[prev_index][1]

                section_data = Section(course_id, df[prev_index:index])
                section_data.get_section_stats()

                prof = Professor(email_addr, course_id, section_data)
                prof.create_message()
                prof.send_message()
                prev_index = index
                print("\n\n")
            prev_id = row[1]


# password reset email
def send_password_reset_email(user):
    """Evan's password reset function"""
    token = user.get_reset_password_token() # generate token for email
    body = "Hello, please follow the link to reset password: " + url_for('resetPassword', token=token, _external=True)
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = user.email
    message["Subject"] = "Password Reset Request"
    message.attach(MIMEText(body, "plain"))
    msg = message.as_string()
    Thread( target = send_email, args = (message['To'], msg) ).start()


send_all_prof_emails()
