from flask import Blueprint, current_app

bp = Blueprint('main', __name__)

from app.main import routes
from flask_apscheduler import APScheduler
from app.main.scheduler import check_dates

scheduler = APScheduler()

class APConfig(object):
    JOBS = [{
        'id': 'deadline-reminder-id',
        'func': check_dates,
        'trigger': 'interval',
        # 'seconds': 2
        'seconds': 10,
        'args': (current_app._get_current_object(),)
    }]
    SCHEDULER_API_ENABLED = True

def start_scheduler(config_class=APConfig):
    current_app.config.from_object(config_class)
    scheduler.init_app(current_app)
    scheduler.start()

start_scheduler()