from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from os import path
from .models import User, Table, Item
from . import db, app
from .settings import DB_NAME

auth = Blueprint('auth', __name__)


@auth.route('/', methods=['POST', 'GET'])
def login():
    if request.method == 'POST' and request.form.get("submit") == "Login":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash("Logged in!", "info")
                if user.is_admin():
                    return redirect(url_for('auth.adminPanel'))
                return redirect(url_for('views.profile'))
            else:
                flash("Incorrect password. Please try again", "error")
        else:
            flash("Username not found. Please try again", "error")
    return render_template("index.html")


@auth.route('/admin-panel', methods=['POST', 'GET'])
def adminPanel():
    if request.method == "POST" and request.form.get("submit") == "Logout":
        return redirect(url_for('auth.logout'))

    user = User.query.filter_by(id=current_user.get_id()).first()
    if user and user.is_admin():
        if request.method == 'POST' and request.form.get("submit") == "submit":
            username = request.form.get('username')
            password = request.form.get('password')
            is_admin = request.form.get("is_admin")
            user = User.query.filter_by(username=username).first()
            if not user and username != "" and password != "":
                new_user = User(username=username, password=generate_password_hash(password, method='sha256'))
                if is_admin is not None:
                    new_user.admin = True
                else:
                    new_user.admin = False
                db_admin = User.query.filter_by(id=1).first()
                db_admin_tables = Table.query.filter_by(user_id=db_admin.get_id()).all()
                for table in db_admin_tables:
                    db_admin_items = Item.query.filter_by(table_id=table.id).all()
                    user_table = Table(user_id=new_user.get_id(), table_name=table.table_name)
                    db.session.add(user_table)
                    for item in db_admin_items:
                        user_item = Item(table_id=user_table.id, item_name=item.item_name)
                        db.session.add(user_item)
                db.session.add(new_user)
            else:
                flash("Could not add user", "error")
        if request.method == 'POST' and request.form.get("submit") == "change_pass":
            username = request.form.get("username")
            password = request.form.get("password")
            user = User.query.filter_by(username=username).first()
            if user:
                if password is not None:
                    user.password = generate_password_hash(password)
                    db.session.add(user)
                    db.session.commit()
                    flash("Changed password for " + username, "info")
                else:
                    flash("Password field is blank", "error")
        db.session.commit()
        return render_template("admin-panel.html")
    else:
        return redirect(url_for('views.profile'))


@auth.route('logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
