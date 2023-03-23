from flask import Blueprint, request, url_for, redirect, render_template, flash
from flask_login import login_required, current_user, login_user, LoginManager

from apps.analyse.models import User
from database.database import doSQLAdmin

analyse = Blueprint('analyse', __name__, template_folder="templates")

@analyse.route('dashboard')
@login_required
def admin():
    return render_template('admin.html', name=current_user.login)

@analyse.route("/login")
def login():
    return render_template("login.html")


@analyse.route('/loginpost', methods=['POST'])
def login_post():
    login = request.form.get('login')
    password = request.form.get('password')
    print(login, password)
    remember = True if request.form.get('remember') else False


    rv = doSQLAdmin("SELECT * FROM user WHERE login = ?", (login,))

    if rv == [] or len(rv) != 1:
        flash('Please check your login details and try again.')
        return redirect(url_for('analyse.login'))
    print(rv[0][2] != password)
    if rv[0][2] != password:
        flash('Please check your login details and try again.')
        return redirect(url_for('analyse.login'))
    # if the above check passes, then we know the user has the right credentials
    user = User(rv[0][0], rv[0][1], rv[0][2])
    login_user(user, remember=remember)
    return redirect(url_for('analyse.admin'))

@analyse.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404