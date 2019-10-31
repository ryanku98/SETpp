from app import app,db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

@app.shell_context_processor
def make_shell_context():
  return {'db': db, 'User': User}

def login(User):
  print("LOGGING IN")
  email_ = input("Email: ")
  user = User.query.filter_by(email=email_).first()
  if user:
    password = input("Password: ")
    if check_password_hash(user.password_hash, password):
      print("logged in")
  else:
    print("user not authorized")
# def get_users()

def register(User):
  print("REGISTERING")
  email_ = input("Email: ")
  password_ = input("Password: ")
  hash_pswd = generate_password_hash(password_)
  print(hash_pswd)
  new_user = User(email=email_, password_hash=hash_pswd)
  db.session.add(new_user)
  db.session.commit()



# User.query.delete()
# add_user('Admin', 'admin@scu.edu', 'password')

if len(User.query.all()) == 0:
  register(User)
  
else:
  login(User)
# print(get_email('Admin'))