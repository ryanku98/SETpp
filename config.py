import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'put-secondary-key-here'

class Config(object):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')       #Flask-SQLAlchemy extension takes location of app's database from SQLALCHEMY_DATABASE_URI config variable
    SQLALCHEMY_TRACK_MODIFICATIONS = False

