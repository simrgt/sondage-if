import json

import mysql.connector
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_wtf import FlaskForm
from wtforms import SelectField
from datetime import timedelta

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config["DEBUG"] = True
app.config['SECRET_KEY']='key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=5)
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True

configDB = {
    'host':"bqpjqiutmrlk6tkmm9ef-mysql.services.clever-cloud.com",
    'user':"usfyvwadlczjc1jj",
    'password':"Jq2Sn2xCIZnqlEOZL1E4",
    'database':"bqpjqiutmrlk6tkmm9ef"
}

# mysql = MySQL(app)
error = "Cette personne à déjà rempli ce sondage"
error2 = "Session expirée"

class Groupe(FlaskForm):
    db = mysql.connector.connect(**configDB)
    c = db.cursor()
    c.execute(f"SELECT alim_grp_code ,alim_grp_nom_fr FROM GroupeAliment")
    groupe = SelectField('groupe', choices=c.fetchall())
    c.execute(f"SELECT alim_ssgrp_code, alim_ssgrp_nom_fr FROM SousGroupeAliment")
    sous_groupe = SelectField('sousGroupe', choices=c.fetchall())
    c.execute(f"SELECT alim_ssssgrp_code, alim_ssssgrp_nom_fr FROM SousSousGroupeAliment")
    sous_sous_groupe = SelectField('sousSousGroupe', choices=c.fetchall())
    c.execute(f"SELECT alim_code, alim_nom_fr FROM Aliment")
    aliment = SelectField('aliment', choices=c.fetchall())
    db.close()




@app.route("/", methods=['GET', 'POST'])
def index():
    if session.get('error') is not None :
        return render_template("index.html", error=session['error'])
    return render_template("index.html")

@app.route("/inscription/", methods=['GET', 'POST'])
def inscription() :
    if request.method == "POST":
        session['nom'] = str(request.form.get("nom")).capitalize()
        session['prenom'] = str(request.form.get("prenom")).capitalize()
        session['mail'] = str(request.form.get("email"))
        print(session['nom'], session['prenom'], session['mail'])
        db = mysql.connector.connect(**configDB)
        c= db.cursor()

        c.execute(f"SELECT nom, prenom, mail FROM Personne WHERE (nom='{session['nom']}' AND prenom='{session['prenom']}' AND mail='{session['mail']})') OR mail='{session['mail']}' ")
        myresult = c.fetchall()
        db.close()
        if myresult == []:
            session.permanent = True
            return redirect(url_for('sondage'))
        else :
            session['error']=error
            return redirect(url_for('index'))
    else :
        if session.permanent is False :
            session['error']=error2
            return redirect(url_for('index'))
    return redirect(url_for('index'))

@app.route("/CGU/")
def CGU():
    return render_template("CGU.html")

@app.route("/sondage/", methods=["POST", "GET"])
def sondage():
    if session.permanent is False :
        return redirect(url_for('inscription'))
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
        form=Groupe()
    return render_template("sondage.html", villes=villes, niveaux=niveaux, form=form)


@app.route('/api/sousGroupe/<groupe>')
def sousGroupe(groupe):
    db = mysql.connector.connect(**configDB)
    c = db.cursor()
    c.execute(f"SELECT alim_ssgrp_code ,alim_ssgrp_nom_fr FROM SousGroupeAliment WHERE idGroupeAliment ={groupe}")
    sous_groupes = c.fetchall()

    sous_groupesArray = []
    for sous_groupe in sous_groupes:
        ssGrp = {}
        ssGrp['id'] = sous_groupe[0]
        ssGrp['name'] = sous_groupe[1]
        sous_groupesArray.append(ssGrp)

    return jsonify({'sousGroupe':sous_groupesArray})

@app.route('/api/sousSousGroupe/<sousGroupe>')
def sousSousGroupe(sousGroupe):
    db = mysql.connector.connect(**configDB)
    c = db.cursor()
    c.execute(f"SELECT alim_ssssgrp_code ,alim_ssssgrp_nom_fr FROM SousSousGroupeAliment WHERE alim_ssgrp_code ={sousGroupe}")
    sous_sous_groupes = c.fetchall()

    sous_sous_groupesArray = []
    for sous_sous_groupe in sous_sous_groupes:
        ssssGrp = {}
        ssssGrp['id'] = sous_sous_groupe[0]
        ssssGrp['name'] = sous_sous_groupe[1]
        sous_sous_groupesArray.append(ssssGrp)

    return jsonify({'sousSousGroupe':sous_sous_groupesArray})

@app.route('/api/aliment/<sousSousGroupe>')
def aliment(sousSousGroupe):
    db = mysql.connector.connect(**configDB)
    c = db.cursor()
    c.execute(f"SELECT alim_code ,alim_nom_fr FROM Aliment WHERE alim_ssssgrp_code ={sousSousGroupe}")
    sous_sous_groupes = c.fetchall()

    sous_sous_groupesArray = []
    for sous_sous_groupe in sous_sous_groupes:
        ssssGrp = {}
        ssssGrp['id'] = sous_sous_groupe[0]
        ssssGrp['name'] = sous_sous_groupe[1]
        sous_sous_groupesArray.append(ssssGrp)

    return jsonify({'aliment':sous_sous_groupesArray})
