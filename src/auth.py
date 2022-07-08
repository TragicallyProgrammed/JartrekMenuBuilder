from flask import Blueprint, render_template, request, redirect, url_for, Response, flash
from flask_login import login_required, logout_user, login_user
from werkzeug.security import check_password_hash
from .models import User

auth = Blueprint('auth', __name__)


@auth.route('/', methods=['POST', 'GET'])
def login():
    try:
        if request.method == "POST" and request.form.get("submit") == "Login":
            username = request.form.get("username").strip()
            password = request.form.get("password").strip()
            db_user = User.query.filter_by(username=username).first()

            if db_user and check_password_hash(db_user.password, password):
                login_user(db_user, remember=True)
                flash("Logged In!", "info")

                if db_user.is_admin():
                    return redirect(url_for('views.adminPanel'))
                return redirect(url_for('views.profile'))
            else:
                flash("Username/Password is incorrect", "error")
                return redirect(url_for("auth.login"))

        return render_template("index.html")

    except Exception as e:  # Catch all exception
        print("Error in Login: ", e)  # Print the exception
        return redirect(url_for("auth.login"))


@auth.route('logout')
@login_required
def logout():
    """Logs out the currently logged-in user"""
    logout_user()
    return redirect(url_for("auth.login"))
