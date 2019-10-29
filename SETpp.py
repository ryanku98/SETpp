from app import app,db
from app.models import User

@app.shell_context_processor
def make_shell_context():
  return {'db': db, 'User': User}

def add_user(username, email):
  new_user = User(username=username, email=email)
  db.session.add(new_user)
  db.session.commit()

add_user('Admin', 'admin@scu.edu')
print(User.query.all())