from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
import os

static_folder = os.path.abspath('static')
db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'login'
bootstrap = Bootstrap()

def create_app(config_class=Config):
    app = Flask(__name__, static_folder=static_folder)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)

    # I SPENT 5 STRAIGHT HOURS DEBUGGING AN ISSUE THAT THIS ONE LINE RESOLVED - rku
    with app.app_context():
        from app.main import bp as main_bp
        app.register_blueprint(main_bp)

    return app

from app import models
