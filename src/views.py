from flask import Blueprint, render_template, request, redirect, url_for, Response, send_from_directory
from flask_login import login_required, current_user
import os

views = Blueprint('views', __name__)
"""Blueprint for views."""

Privilege_Levels = ['Customer', 'Technician', 'Super Admin']
"""List of Privilege Levels for users. The index corresponds to the level value."""


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
    return render_template("profile.html", user={'username': current_user.username, 'privilegeLevel': current_user.privilege_level})


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

        return render_template("admin-panel.html", user={'username': current_user.username, 'privilegeLevel': current_user.privilege_level}, PrivilegeLevels=Privilege_Levels)

    except Exception as e:
        print("Exception: ", str(e))
        return Response(status=500)


@views.route('/favicon.ico')
def favicon():
    """
    Endpoint for favicon
    """
    return send_from_directory(os.path.join(views.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@views.route('/help')
def help_screen():
    """
    Endpoint for rendering the help screen.

    Returns
    -------
    render_template
        Ships the html for help-page.
    """
    return render_template("help-page.html")
