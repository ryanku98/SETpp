from app import app,db
from app.models import User
from werkzeug.security import generate_password_hash, check_password_hash

@app.shell_context_processor
def make_shell_context():
  return {'db': db, 'User': User}

# User.query.delete()
# add_user('Admin', 'admin@scu.edu', 'password')

# if len(User.query.all()) == 0:
#   register(User)
# <<<<<<< HEAD
  
# =======
# 
# >>>>>>> bf34d9b5e3b47819a8efb4c96e8024ab3fb47a0d
# else:
#   login(User)
# print(get_email('Admin'))