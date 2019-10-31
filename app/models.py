from datetime import datetime
from app import db   #adds database object defined in init.py


class User(db.Model):   #inherits from db.Model, a base class for all models in Flask-SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)      #defines fields as class variables, or instances of db.Column class, taking field type as an argument
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    # posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

# class Post(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     body = db.Column(db.String(140))
#     timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))       #references id value form user table

#     def __repr__(self):
#         return '<Post {}>'.format(self.body)