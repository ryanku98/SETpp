import os
import csv
import smtplib
import email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

roster_file = os.path.join('documents', 'roster.csv')
# List of headers of roster file
roster_headers = ['Term', 'Class Nbr', 'Subject', 'Catalog', 'Title', 'Section', 'Instructor', 'Instructor Email', 'Student ID', 'Student', 'Email', 'Tot Enrl', 'Unit Taken', 'Grade', 'Campus', 'Location', 'Add Dt', 'Drop Dt', 'Comb Sect', 'Career', 'Component', 'Session', 'Class Type', 'Grade Base']
student_id_i = 8
course_id_i = 1
instructor_email_i = 7

class studentSystem:

  def __init__(self, list1, list2, list3):
    self.name_list = list1
    self.email_list = list2
    self.courses = list3

  def parseList(self):
    with open(roster_file, newline='') as csvfile:
      spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
      for row in spamreader:
        self.name_list.append(row[8])  # emails.csv: 0
        self.email_list.append(row[9]) # emails.csv: 1
        self.courses.append(row[1])


def sendemails(system):
    port = 587  # For SSL
    smtp_server = "smtp.gmail.com"
    
    with smtplib.SMTP(smtp_server, port) as smtp:  #Opens connection with variable name "server"
        smtp.ehlo()   #Identifies with mail server we are using
        smtp.starttls()   #Start encrypting traffic
        smtp.ehlo()
        
        sender_email = "setsystempp@gmail.com"
        sender_pswd = "setpp_coen174"
        smtp.login(sender_email, sender_pswd)

        i = 0
        for student_email in system.email_list[1:]:
            i = i + 1
            
            msg = make_student_message(sender_email, student_email, system.name_list[i], students.courses[i])
            smtp.sendmail(sender_email, student_email, msg)


def make_student_message(sender_email, student_email, name, courseid):
    body = "Hello " + name + ",\nPlease fill your lab evaluations for course #" + courseid + " out at the following link: google.com"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = student_email
    message["Subject"] = name + ", please fill out your lab evaluations"
    message.attach(MIMEText(body, "plain"))
    msg = message.as_string()
    
    return msg
    
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

def main():
    students = studentSystem([], [], [])
    students.parseList()
    sendemails(students)
    
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
