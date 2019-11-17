from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
import os

static_folder = os.path.abspath('static')
application = Flask(__name__, static_folder = static_folder)
app = application
app.config.from_object(Config)
db = SQLAlchemy(app)  #db object that represents the database
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)

from app import routes, models  # module will define structure of the database

import atexit
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app.models import Deadline, Reminder, log_header
from app.emails import send_all_student_emails, send_all_prof_emails

# START OF SCHEDULER CODE
scheduler = BackgroundScheduler()
@scheduler.scheduled_job('interval', seconds=10, id='deadline-reminder-id')
def check_dates():
    """Check existing deadlines and reminders in the database, executes any corresponding action if one has passed"""
    now = datetime.utcnow()
    d_sent = False
    r_sent = False
    deadline = Deadline.query.first()
    reminders = Reminder.query.order_by(Reminder.datetime).all()
    # if deadline exists, check if already passed
    if deadline is not None and not deadline.is_valid(now) and not deadline.executed:
        # send results
        # app.app_context() needed because Flask can't retrieve app context for Jinja's render_template() when this is called here
        print(log_header('AUTOMATED EMAILS'))
        with app.app_context():
            send_all_prof_emails()
            deadline.executed = True
            db.session.commit()
        d_sent = True
    else:
        print(deadline.executed)
    for reminder in reminders:
        if not reminder.is_valid(now):
            # if no emails have been sent yet
            if not d_sent and not r_sent:
                print(log_header('AUTOMATED EMAILS'))
            # if a reminder has been sent already, other reminders that may have passed within the same interval should not trigger another reminder (and should be also removed)
            if not r_sent:
                # app.app_context() needed because Flask can't retrieve app context for Jinja's render_template() when this is called here
                with app.app_context():
                    send_all_reminder_emails()
                r_sent = True
            with app.app_context():
                db.session.delete(reminder)
                db.session.commit()

print('Scheduler starting...')
scheduler.start()
# shut down schedule when app exits
atexit.register(lambda: scheduler.shutdown())
# END OF SCHEDULER CODE
