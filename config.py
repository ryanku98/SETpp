import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'super-secret-coen174-key'
    # Flask-SQLAlchemy extension takes location of app's database from SQLALCHEMY_DATABASE_URI config variable
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
    'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SERVER_NAME = os.environ.get('SERVER_NAME') or 'localhost:5000'

    # email stuff
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587 # for starttls()
    MAIL_ADDRESS = 'setsystempp@gmail.com'
    MAIL_PASSWORD = 'setpp_coen174'

    DEVELOPERS = ('a1morales', 'eejohnson', 'rku')
    # key to wipe entire database (mainly to make it easy for devs when deployed on a cloud platform)
    OVERRIDE_PW = os.environ.get('OVERRIDE_PW') or 'super-secret-override-pw'
    LOG_TO_STDOUT = os.environ.get('LOG_TO_STDOUT')
