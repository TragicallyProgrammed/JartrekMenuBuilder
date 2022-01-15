from flask import Blueprint, render_template, request, redirect, url_for, flash, Response
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from os import path
from .models import User, Table, Item
from . import db, app

auth = Blueprint('auth', __name__)


@auth.route('/', methods=['POST', 'GET'])
def login():
    """Login endpoint. Index.html"""
    try:
        if request.method == 'POST':  # If a post request is sent...
            username = request.form.get("username")  # Get username from client
            password = request.form.get("password")  # Get password from client
            db_user = User.query.filter_by(username=username).first()  # Find given user in database

            if check_password_hash(db_user.password, password):  # If the given password matches the stored password
                login_user(db_user, remember=True)  # Login the given user
                flash("Logged In!", "info")  # Alert user that they have successfully logged in

                if db_user.is_admin():  # If the user is an admin...
                    return redirect(url_for('auth.adminPanel'))  # Redirect to the admin panel

                return redirect(url_for('views.profile'))  # Otherwise, redirect to profile

            else:  # If the given password does not match the stored password...
                flash("Incorrect Password!", "error")  # Alert client that the password is incorrect

    except AttributeError as e:
        flash("Could not find user!", "error")  # Alerts client that the user does not exist
        print("Attribute Error While Loggin In...")  # Prints to console that there was an error
        print("Error: ", e)  # Print error

    except Exception as e:  # Catch all exception
        print("Error in Login: ", e)  # Print the exception
        return Response(status=500)  # Return error code to client

    return render_template("index.html")  # If the request is not post, return the page


@auth.route('/admin-panel', methods=['POST', 'GET'])
@login_required
def adminPanel():
    """Admin Panel Endpoint. Should be redirected to automatically if the user is an admin"""
    try:
        db_user = User.query.filter_by(id=current_user.get_id()).first()  # Get the database entry of the currently logged-in user

        if db_user.is_admin():  # If the user is an admin...
            if request.method == 'POST':  # If the request is a post...
                print(request.form.get("submit") == "change_pass")
                if request.form.get('submit') == 'Logout':  # If the request form is logout...
                    return redirect(url_for('auth.logout'))  # returns redirect for logging out

                # This block of code allows for the addition of new users
                if request.form.get("submit") == "submit":  # If the request form is submit...
                    username = request.form.get('username')  # Get the username from the form
                    password = request.form.get('password')  # Get the password from the form
                    is_admin = request.form.get('is_admin')  # Get if the user is an admin from the form
                    db_user = User.query.filter_by(username=username).first()  # Search the db for a user of the same username

                    if not db_user and username != "" and password != "":  # If the username and password are not blank and the user is not found already...
                        new_user = User(username=username, password=generate_password_hash(password, method='sha256'), admin=False)  # Create a new user with admin set to false by default
                        if is_admin is not None:  # If is_admin has been checked...
                            new_user.admin = True  # Set the new user to be an admin

                        db.session.add(new_user)  # Add the new user to the session

                    else:  # If the user is found, or if username or password is blank...
                        flash("Could not add user!", "error")  # Send error to client

                if request.form.get("submit") == "change_pass":  # If the request form is to change passwords...
                    username = request.form.get('username')  # Get the username from the form
                    password = request.form.get('password')  # Get the password from the form
                    db_user = User.query.filter_by(username=username).first()  # Search the db for a user of the same username

                    if db_user:  # If the user exists in the database...
                        if password is not None:  # If the given password is not blank...
                            db_user.password = generate_password_hash(password)  # Update user with the given password
                            db.session.add(db_user)  # Add changes to be committed
                            flash("Changed password for " + username, "info")  # Alert client that password has changed

            db.session.commit()  # Commit changes to database

        else:  # If the currently logged-in user is not an admin...
            flash("No Admin Privileges", "error")  # Sends error to client
            return redirect(url_for('auth.logout'))  # Logout the current user

    except Exception as e:  # Catch all exception
        print("Exception: ", e)  #

    return render_template("admin-panel.html", username=current_user.username)  # If the request is not post, return the page


@auth.route('logout')
@login_required
def logout():
    """Logs out the currently logged-in user"""
    logout_user()
    return redirect(url_for("auth.login"))
