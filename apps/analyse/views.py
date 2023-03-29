import datetime

from flask import Blueprint, request, url_for, redirect, render_template, flash
from flask_login import login_required, login_user


from apps.analyse.models import User
from database.database import doSQLAdmin, doSqlWithoutEffect

analyse = Blueprint('analyse', __name__, template_folder="templates")

def getData():
    data = doSqlWithoutEffect("SELECT COUNT(id), date FROM Sondage GROUP BY date ORDER BY date DESC")
    print(data)
    label = []
    value = []
    for i in range(len(data)):
        data[i] = list(data[i])
        data[i][1] = data[i][1].strftime("%d/%m/%Y")
        label.append(data[i][1])
        value.append(data[i][0])
    print(data)
    return label, value

@analyse.route('admin')
@login_required
def admin():
    label, value = getData()
    return render_template('admin.html', label=label, nbSondage=value)

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
        flash('Merci de vérifié vos identifiants.')
        return redirect(url_for('analyse.login'))
    print(rv[0][2] != password)
    if rv[0][2] != password:
        flash('Merci de vérifié vos identifiants.')
        return redirect(url_for('analyse.login'))
    # if the above check passes, then we know the user has the right credentials
    user = User(rv[0][0], rv[0][1], rv[0][2])
    login_user(user, remember=remember)
    return redirect(url_for('analyse.admin'))

@analyse.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404