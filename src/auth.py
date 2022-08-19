from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, logout_user, login_user
from werkzeug.security import check_password_hash
from .models import User

auth = Blueprint('auth', __name__)
"""Blueprint login endpoints"""


@auth.route('/', methods=['POST', 'GET'])
def login():
    """
    Endpoint for the login screen

    This endpoint acts as the homepage for the site.
    It contains the login form for both admin users and non-admin users.

    Raises
    -----
    Exception
        Prints the error and returns a redirect to this page.

    Returns
    -------
    redirect
        If the user that is logging in has 'admin' set as true, a redirect to views.adminPanel is returned.

        If the user that is logging in has 'admin' set as false, a redirect to views.profile is returned.

        If the login failed, a redirect to this page is sent.
    render_template
        Ships the html for index.html.

    """
    try:
        if request.method == "POST" and request.form.get("submit") == "Login":
            username = request.form.get("username").strip()
            password = request.form.get("password").strip()
            db_user = User.query.filter_by(username=username).first()

            if db_user and check_password_hash(db_user.password, password):
                login_user(db_user, remember=True)
                flash("Logged In!", "info")

                if db_user.privilege_level > 0:
                    return redirect(url_for('views.adminPanel'))
                return redirect(url_for('views.profile'))
            else:
                flash("Username/Password is incorrect", "error")
                return redirect(url_for("auth.login"))

        return render_template("index.html")

    except Exception as e:
        print("Error in Login: ", e)
        return redirect(url_for("auth.login"))


@auth.route('logout')
@login_required
def logout():
    """
    Endpoint for logging the currently logged-in user out.

    Returns
    -------
    redirect
        Redirects to auth.login.
    """
    logout_user()
    return redirect(url_for("auth.login"))
