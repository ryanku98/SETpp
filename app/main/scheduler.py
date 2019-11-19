from app import db
from app.models import Deadline, Reminder, log_header
from app.emails import send_all_student_emails, send_all_prof_emails
from datetime import datetime

def check_dates(app):
    """Check existing deadlines and reminders in the database, executes any corresponding action if one has passed"""
    now = datetime.utcnow()

    with app.app_context():
        deadline = db.session.query(Deadline).first()
        # if deadline exists, check if already passed
        if deadline is not None and not deadline.is_valid(now) and not deadline.executed:
            print(log_header('AUTOMATED EMAILS'))
            send_all_prof_emails()
            deadline.executed = True
            db.session.commit()
        else:
            reminders = db.session.query(Reminder).order_by(Reminder.datetime).all()
            r_sent = False
            for reminder in reminders:
                if not reminder.is_valid(now):
                    # if no emails have been sent yet
                    if not r_sent:
                        print(log_header('AUTOMATED EMAILS'))
                        # with app.app_context():
                        send_all_reminder_emails()
                        r_sent = True
                    # if a reminder has been sent already, other reminders that may have passed within the same interval should not trigger another reminder (and should be also removed)
                    db.session.delete(reminder)
                    db.session.commit()

