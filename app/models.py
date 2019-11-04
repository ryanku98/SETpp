from datetime import datetime
from app import app, db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from time import time

# inherits from db.Model, a base class for all models in Flask-SQLAlchemy
class User(UserMixin, db.Model):
    # defines fields as class variables, or instances of db.Column class, taking field type as an argument
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600): #Encodes {info} and returns a token
        return jwt.encode(
            {'reset_password': self.id, 'exp': time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256').decode('utf-8')

    def verify_reset_password_token(token): #Decodes token using SECRET_KEY defined in app config class
        try:
            id = jwt.decode(token, app.config['SECRET_KEY'],
            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)



    def __repr__(self):
        return '<User {}>'.format(self.email)

@login.user_loader
def load_user(id):
    return User.query.get(int(id))
