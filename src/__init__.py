"""
Package containing the Jartrek Menu Builder Website

The Jartrek Menu Builder is a web application designed for usage in VFW's, American Legion's, ect.
Upon purchasing a new Jartrek system, the customer will be given a login for the website and will
be asked to fill out the provided tables with what they sell, and for how much. In addition to
menu items, the customer will be asked to provide any paid ins and paid outs the club does through
the register, and a list of all employees to be added to the Jartrek database. This data can then
be collected for building out the customer's database that will run Jartrek.

References
----------
www.github.com/NeonProgrammed/JartrekMenuBuilder

Examples
--------
from src import create_app

app = create_app(False)

if __name__ == '__main__':
    app.run()

In this example, we are importing the create_app function from the package and then executing run to start the server
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from os import path

app = Flask(__name__)
"""Main Flask application instance"""
db = SQLAlchemy()
"""SQLAlchemy for sqlite database"""
login_manager = LoginManager()
"""Login manager for flask"""


def create_app(debug, local_db):
    """
    Initializes all fields required for flask.

    Uses data from .env file to set a key, the uri for the database, and the user data for the database.
    It then creates a new user if the website detects a new database with the following information:
    username: admin
    password: admin

    Parameters
    ----------
    debug: bool
        Sets the debug flag for flask. True will activate the debugger and False will deactivate it.
    local_db: bool
        Creates a local database if set to true. If false, the site tries to connect to a MariaDB.

    Returns
    -------
    Flask
        Returns the flask application
    """
    from .views import views
    from .db_views import db_views
    from .auth import auth
    from .models import User
    from .settings import KEY, DB_NAME, DB_USER, DB_PASSWORD

    app.config['SECRET_KEY'] = KEY
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['DEBUG'] = debug
    app.config["CACHE_TYPE"] = "null"

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(db_views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    if local_db:
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'

        db.init_app(app)

        if not path.exists('src/' + DB_NAME):
            db.create_all(app=app)
            print("Created Database")
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = f'mariadb+mariadbconnector://{DB_USER}:{DB_PASSWORD}@localhost:3306/{DB_NAME}'

        db.init_app(app)

        db.create_all(app=app)

    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

