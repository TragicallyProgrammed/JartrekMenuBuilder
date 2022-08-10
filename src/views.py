from flask import Blueprint, render_template, request, redirect, url_for, Response
from flask_login import login_required, current_user

views = Blueprint('views', __name__)
"""Blueprint for views."""


@views.route('profile', methods=['POST', 'GET'])
@login_required
def profile():
    """
    Endpoint for user profile.

    This endpoint should only be reached via auth.login
    only if the user that is logging in has 'admin' set to
    false in the database.

    Returns
    -------
    redirect
        Redirects to auth.logout if a request to logout is sent.
    render_template
        Ships the html for profile.html.
    """
    if request.method == "POST" and request.form.get("submit") == "Logout":
        return redirect(url_for('auth.logout'))
    return render_template("profile.html", username=current_user.username)


@views.route('admin-panel', methods=['POST', 'GET'])
@login_required
def adminPanel():
    """
    Endpoint for admin panel.

    This endpoint should only be reached via auth.login
    only if the user that is logging in has 'admin' set to
    true in the database.

    Returns
    -------
    redirect
        Redirects to auth.logout if a request to logout is sent.
    render_template
        Ships the html for admin-panel.html.

    Raises
    ------
    Exception
        If any errors occur during the redirect or rendering of html, print the error and return error status.
    """
    try:
        if request.method == "POST" and request.form.get("submit") == "Logout":
            return redirect(url_for('auth.logout'))

        return render_template("admin-panel.html", username=current_user.username)

    except Exception as e:
        print("Exception: ", str(e))
        return Response(status=500)
