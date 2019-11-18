# from app import app, db
from app import create_app, db
from app.models import User, Section, Student, Result, Deadline, Reminder

app = create_app()

@app.shell_context_processor
def make_shell_context():
  return {'db': db, 'User': User, 'Section': Section, 'Student': Student, 'Result': Result, 'Deadline': Deadline, 'Reminder': Reminder}
