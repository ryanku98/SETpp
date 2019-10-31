# Professor emailing
# very similar to parse.py file which parses through students, this parses and emails the professors
# we need to somehow display the results inside an email_list
# html?


class professorSystem:
    
  def __init__(self, list1, list2):
    self.name_list = list1
    self.email_list = list2

  def parseList(self, list1, list2):
    with open('registration.csv', newline='') as csvfile:
      spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
      for row in spamreader:
        self.name_list.append(row[6])  # change to row 6
        self.email_list.append(row[7]) # change to row 7


prof_system = professorSystem([], [])
prof_system.parseList()


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
    for prof_email in prof_system.email_list:
        name = prof_system.name_list[i]
        i = i + 1
        
        subject = name + ", here are the results of lab teaching evaluations"
        body = "Hello " + name + ",\nBelow is your TA's teaching evaluation results."
        
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = prof_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))
        msg = message.as_string()
        smtp.sendmail(sender_email, prof_email, msg) 
