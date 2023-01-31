
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
import requests
import simplejson
import json

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config["DEBUG"] = True
configDB = {
    'host':"bqpjqiutmrlk6tkmm9ef-mysql.services.clever-cloud.com",
    'user':"usfyvwadlczjc1jj",
    'password':"Jq2Sn2xCIZnqlEOZL1E4",
    'database':"bqpjqiutmrlk6tkmm9ef"
}

# mysql = MySQL(app)
error = "Cette personne à déjà rempli ce sondage"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/inscription/", methods=['GET', 'POST'])
def inscription() :
    if request.method == "POST":
        nom = str(request.form.get("nom")).capitalize()
        prenom = str(request.form.get("prenom")).capitalize()
        mail = str(request.form.get("prenom"))
        db = mysql.connector.connect(**configDB)
        c= db.cursor()

        c.execute(f"SELECT nom, prenom, mail FROM Personne WHERE nom='{nom}' AND prenom='{prenom}' AND mail='{mail}'")
        myresult = c.fetchall()
        db.close()
        if myresult == []:
            return redirect(url_for('sondage'))
        else :
            return render_template("index.html", error=error)

@app.route("/CGU/")
def CGU():
    return render_template("CGU.html")

@app.route("/sondage/", methods=["POST", "GET"])
def sondage():
    if request.method == "GET":
        uri = "https://geo.api.gouv.fr/communes"
        try:
            uResponse = requests.get(uri)
        except requests.ConnectionError:
            return "Connection Error"
        Jresponse = uResponse.text
        data = json.loads(Jresponse)
        villes = []
        for i in data:
            villes.append(i['nom'])
        db = mysql.connector.connect(**configDB)
        c = db.cursor()

        c.execute(f"SELECT NiveauScolaire FROM StatutScolaire")
        niveaux = c.fetchall()
        db.close()
        print(type(niveaux))


    return render_template("sondage.html", villes=villes, niveaux=niveaux)
