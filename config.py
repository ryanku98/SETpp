import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-coen174-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')       #Flask-SQLAlchemy extension takes location of app's database from SQLALCHEMY_DATABASE_URI config variable
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # email stuff
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587 # for starttls()
    MAIL_PASSWORD = 'setpp_coen174'
    ADMIN = 'setsystempp@gmail.com'
