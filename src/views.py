from flask import Blueprint, render_template, request, redirect, url_for, Response
from flask_login import login_required, current_user

views = Blueprint('views', __name__)


# Profile Page Endpoint
@views.route('profile', methods=['POST', 'GET'])
@login_required
def profile():
    if request.method == "POST" and request.form.get("submit") == "Logout":
        return redirect(url_for('auth.logout'))
    return render_template("profile.html", username=current_user.username)


@views.route('admin-panel', methods=['POST', 'GET'])
@login_required
def adminPanel():
    """Admin Panel Endpoint. Should be redirected to automatically if the user is an admin"""
    try:
        if request.method == "POST" and request.form.get("submit") == "Logout":
            return redirect(url_for('auth.logout'))

        return render_template("admin-panel.html", username=current_user.username)

    except Exception as e:  # Catch all exception
        print("Exception: ", str(e))
        return Response(status=200)
