from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path

db = SQLAlchemy()
app = Flask(__name__)
login_manager = LoginManager()


def create_app():
    from .views import views
    from .auth import auth
    from .models import User
    from.settings import KEY, TRACK_MODIFICATIONS, ENVIROMENT, DEBUG, DB_NAME

    app.config['SECRET_KEY'] = KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = TRACK_MODIFICATIONS
    app.config['ENV'] = ENVIROMENT
    app.config['DEBUG'] = DEBUG
    app.config["CACHE_TYPE"] = "null"
    db.init_app(app)

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    create_database(app)

    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app


def create_database(app):
    from .settings import DB_NAME
    if not path.exists('src/' + DB_NAME):
        db.create_all(app=app)
