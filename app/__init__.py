from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

application = Flask(__name__)
app = application
app.config.from_object(Config)
db = SQLAlchemy(app)  #db object that represents the database
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)

import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app.models import Deadline, Reminder
from app.survey import is_valid_datetime
from app.emails import send_all_student_emails, send_all_prof_emails

scheduler = BackgroundScheduler()
@scheduler.scheduled_job('interval', seconds=10, id='deadline-reminder-id')
def check_dates():
    """Check existing deadlines and reminders in the database, executes any corresponding action if one has passed"""
    now = datetime.utcnow()
    print('-------------------------------------------------')
    print('Checking deadlines at {}'.format(now))

    deadline = Deadline.query.first()
    # if deadline exists, check if already passed
    if deadline is not None:
        print('DEADLINE: {}'.format(deadline))
        if not is_valid_datetime(deadline.datetime, now):
            # send results and delete deadline
            send_all_prof_emails()
            Deadline.query.delete()
    else:
        print('DEADLINE NOT FOUND')

    reminders = Reminder.query.all()
    print('TIME NOW: {}'.format(now))
    print('REMINDERS: {}'.format(reminders))
    # sent flag: if a reminder has been sent already, other reminders that may have passed within the same interval should not trigger another reminder (and thus should be removed)
    sent = False
    for reminder in reminders:
        if not is_valid_datetime(reminder.datetime, now):
            # send emails only if a reminder has not been sent yet
            if not sent:
                # TODO: CHANGE TO SEND REMINDER EMAIL
                send_all_student_emails()
                sent = True
            db.session.delete(reminder)
            print('Reminder {} sent.'.format(reminder))
    db.session.commit()

print('Scheduler starting...')
scheduler.start()

# shut down schedule when app exits
atexit.register(lambda: scheduler.shutdown())

from app import routes, models  #module will define structure of the database

if __name__ == '__main__':
    print('Scheduler starting...')
    scheduler.start()
    # pass
