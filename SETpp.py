from app import app,db
from app.models import User

@app.shell_context_processor
def make_shell_context():
  return {'db': db, 'User': User}

def add_user(username_, email_, password_):
  if not User.query.filter_by(username='Admin').first():
    new_user = User(username=username_, email=email_, password_hash=password_)
    db.session.add(new_user)
    db.session.commit()

def get_email(username_):
  user = User.query.filter_by(username=username_)
  return user.first().email

def hash_pass(password):
  return password

User.query.delete()
add_user('Admin', 'admin@scu.edu', 'password')
print(User.query.all())
print(get_email('Admin'))