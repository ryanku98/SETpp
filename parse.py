# This script will parse the student email roster
import csv
import smtplib
import email
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class studentSystem:

  def __init__(self, list1, list2):
    self.name_list = list1
    self.email_list = list2

  def parseList(self):
    with open('emails.csv', newline='') as csvfile:
      spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
      for row in spamreader:
        self.name_list.append(row[0])  
        self.email_list.append(row[1])


system = studentSystem([], [])
system.parseList()


port = 587  # For SSL
smtp_server = "smtp.gmail.com"
with smtplib.SMTP(smtp_server, port) as smtp:  #Opens connection with variable name "server"
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    
    sender_email = "setsystempp@gmail.com"
    sender_pswd = "setpp_coen174"
    smtp.login(sender_email, sender_pswd)

    i = 0
    for student_email in system.email_list:
        name = system.name_list[i]
        i = i + 1
        
        subject = name + ", please fill out your lab evaluations"
        link = "google.com"
        body = "Hello " + name + ",\nplease fill your lab evaluations out at the following link: " + link
        
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = student_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        msg = message.as_string()
        smtp.sendmail(sender_email, student_email, msg)

