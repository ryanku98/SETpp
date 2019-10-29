# This script will parse the student email roster
import csv
import smtplib

class studentSystem:

  def __init__(self, list):
    self.email_list = list

  def parseList(self):
    with open('emails.csv', newline='') as csvfile:
      spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
      for row in spamreader:
        self.email_list.append(row[1])
    # print(email_list)


system = studentSystem([])
system.parseList()



port = 587  # For SSL
smtp_server = "smtp.gmail.com"


receiver_email = "eejohnson@scu.edu"
# password = input("Type your password and press enter: ")


# context = ssl.create_default_context()
with smtplib.SMTP(smtp_server, port) as smtp:  #Opens connection with variable name "server"
    smtp.ehlo()   #Identifies with mail server we are using
    smtp.starttls()   #Start encrypting traffic
    smtp.ehlo()
    
    sender_email = "setsystempp@gmail.com"
    sender_pswd = "setpp_coen174"
    smtp.login(sender_email, sender_pswd)

    message = """\
      Subject: Hi there

      Please fill out the attached evaluation"""

    
    for student_email in system.email_list:
      smtp.sendmail(sender_email, student_email, message)




