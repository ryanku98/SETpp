from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail

application = Flask(__name__)

app = application

app.config.from_object(Config)
db = SQLAlchemy(app)  #db object that represents the database
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
mail = Mail(app)

from app import routes, models  #module will define structure of the database
