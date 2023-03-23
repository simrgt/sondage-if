from flask import Blueprint, request, url_for, redirect, render_template, session
from database.database import doSqlWithoutEffect

main = Blueprint('main', __name__, template_folder="templates")


@main.route("/", methods=['GET', 'POST'])
def index():
    doSqlWithoutEffect("SELECT * FROM Personne")
    if session.get('error') is not None :
        return render_template("index.html", error=session['error'])
    if session.get('sondage') is not None :
        message = session['sondage']
        session.clear()
        return render_template("index.html", error=message)

    return render_template("index.html")


@main.route("/CGU")
def CGU():
    return render_template("CGU.html")

@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


# mysql = MySQL(app)
error = "Cette personne à déjà rempli ce sondage"
error2 = "Session expirée"

@main.route("/inscription", methods=['POST'])
def inscription() :
    if request.method == "POST":
        session['nom'] = str(request.form.get("nom")).capitalize()
        session['prenom'] = str(request.form.get("prenom")).capitalize()
        session['mail'] = str(request.form.get("email"))
        print(session['nom'], session['prenom'], session['mail'])
        myresult = doSqlWithoutEffect(f"SELECT nom, prenom, mail FROM Personne WHERE (nom='{session['nom']}' AND prenom='{session['prenom']}' AND mail='{session['mail']})') OR mail='{session['mail']}' ")
        if myresult == []:
            session.permanent = True
            return redirect(url_for('sondage.index'))
        else :
            session['error']=error
            return redirect(url_for('index'))
    else :
        if session.permanent is False :
            session['error']=error2
            return redirect(url_for('index'))
    return redirect(url_for('index'))