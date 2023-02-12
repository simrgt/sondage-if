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

def doSql(sql):
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=1, **configDB)
    try :
        db = connection_pool.get_connection()
        c = db.cursor()
        c.execute(sql)
        result = c.fetchall()
        c.close()
        db.commit()
        db.close()
    except mysql.connector.Error as e:
        return doSql(sql)
    return result

class Groupe(FlaskForm):
    groupe = SelectField('groupe', choices=[('Non Selectionné','Non Selectionné')] + doSql(f"SELECT alim_grp_code ,alim_grp_nom_fr FROM GroupeAliment"))
    sous_groupe = SelectField('sousGroupe')
    sous_sous_groupe = SelectField('sousSousGroupe')
    aliment = SelectField('aliment')

    def personnaliser(self,s,i):
        self.groupe.name = "groupe_" + str(s) + str(i)
        self.sous_groupe.name = "sous_groupe_" + str(s) + str(i)
        self.sous_sous_groupe.name = "sous_groupe_" + str(s) + str(i)
        self.aliment.name = "aliment_" + str(s) + str(i)
        return self

@app.route("/", methods=['GET', 'POST'])
def index():
    if session.get('error') is not None :
        return render_template("index.html", error=session['error'])
    if session.get('sondage') is not None :
        message = session['sondage']
        session.clear()
        return render_template("index.html", error=message)

    return render_template("index.html")

@app.route("/inscription", methods=['POST'])
def inscription() :
    if request.method == "POST":
        session['nom'] = str(request.form.get("nom")).capitalize()
        session['prenom'] = str(request.form.get("prenom")).capitalize()
        session['mail'] = str(request.form.get("email"))
        print(session['nom'], session['prenom'], session['mail'])
        myresult = doSql(f"SELECT nom, prenom, mail FROM Personne WHERE (nom='{session['nom']}' AND prenom='{session['prenom']}' AND mail='{session['mail']})') OR mail='{session['mail']}' ")
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

@app.route("/CGU")
def CGU():
    return render_template("CGU.html")

@app.route("/sondage", methods=["POST", "GET"])
def sondage():
    if session.permanent is False :
        return redirect(url_for('inscription'))
    if request.method == "GET" or request.method == "POST":
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
        niveaux = doSql(f"SELECT NiveauScolaire FROM StatutScolaire")
        formMatin=[]
        formSoir=[]
        for i in range(5):
            formMatin.append(Groupe().personnaliser("matin",i))
            formSoir.append(Groupe().personnaliser("soir",i))
        if request.args.get("values") != None:
            return render_template("sondage.html", villes=villes, niveaux=niveaux, formMatin=formMatin, formSoir=formSoir, values=request.args.get("values"))
        else:
            return render_template("sondage.html", villes=villes, niveaux=niveaux, formMatin=formMatin, formSoir=formSoir, values=None)
    return redirect(url_for('inscription'))


@app.route('/api/sousGroupe/<groupe>')
def sousGroupe(groupe):
    sous_groupes = doSql(f"SELECT alim_ssgrp_code ,alim_ssgrp_nom_fr FROM SousGroupeAliment WHERE idGroupeAliment ={groupe}")
    sous_groupesArray = []
    for sous_groupe in sous_groupes:
        ssGrp = {}
        ssGrp['id'] = sous_groupe[0]
        ssGrp['name'] = sous_groupe[1]
        sous_groupesArray.append(ssGrp)

    return jsonify({'sousGroupe':sous_groupesArray})

@app.route('/api/sousSousGroupe/<sousGroupe>')
def sousSousGroupe(sousGroupe):
    sous_sous_groupes = doSql(f"SELECT alim_ssssgrp_code ,alim_ssssgrp_nom_fr FROM SousSousGroupeAliment WHERE alim_ssgrp_code ={sousGroupe}")

    sous_sous_groupesArray = []
    for sous_sous_groupe in sous_sous_groupes:
        ssssGrp = {}
        ssssGrp['id'] = sous_sous_groupe[0]
        ssssGrp['name'] = sous_sous_groupe[1]
        sous_sous_groupesArray.append(ssssGrp)

    return jsonify({'sousSousGroupe':sous_sous_groupesArray})

@app.route('/api/aliment/<sousSousGroupe>')
def aliment(sousSousGroupe):

    sous_sous_groupes = doSql(f"SELECT alim_code ,alim_nom_fr FROM Aliment WHERE alim_ssssgrp_code ={sousSousGroupe}")

    sous_sous_groupesArray = []
    for sous_sous_groupe in sous_sous_groupes:
        ssssGrp = {}
        ssssGrp['id'] = sous_sous_groupe[0]
        ssssGrp['name'] = sous_sous_groupe[1]
        sous_sous_groupesArray.append(ssssGrp)

    return jsonify({'aliment':sous_sous_groupesArray})


def validate_sondage_form(form):
    form.data={}
    form.errors={}
    form_age = form.get('age')
    if form_age is None:
        form.errors['age'] = "Vous devez renseigner votre age"
    else:
        form.data['age'] = form_age

    form_ville = form.get('ville').capitalize()
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
    if form_ville not in villes:
        form.errors['ville'] = "Vous devez renseigner une ville valide"
    else:
        form.data['ville'] = form_ville

    for i in form.keys():
        print(i, form.get(i))
    form_niveau = form.get('statut')
    if form_niveau is None:
        form.errors['niveau'] = "Vous devez renseigner votre niveau scolaire"
    else:
        form.data['niveau'] = form_niveau

    if form.get('RMatin') == 'on':
        form_matin = []
        for i in range(5):
            if form.get(f"groupe_matin{i}") != "Non Selectionné":
                form_matin.append(form.get(f"aliment_matin{i}"))
            else:
                break
        form.data['matin'] = form_matin
    else:
        form.data['matin'] = [None,None,None,None,None]
    if form.get('RSoir') == 'on':
        form_soir = []
        for i in range(5):
            if form.get(f"groupe_soir{i}") != "Non Selectionné":
                form_soir.append(form.get(f"aliment_soir{i}"))
            else :
                break
        form.data['soir'] = form_soir
    else:
        form.data['soir'] = [None,None,None,None,None]


    print(form.data['matin'])
    print(len(form.errors))
    return len(form.errors) == 0


@app.route('/sondage/verifier', methods=['POST'])
def verifierSondage():
    if session.permanent is False :
        return redirect(url_for('inscription'))
    if request.method == "POST":
        if not validate_sondage_form(request.form):
            return redirect(url_for('sondage', values=request.form))
        session['ville']=request.form.data['ville']
        session['age']=request.form.data['age']
        session['niveau']=request.form.data['niveau']
        session['matin']=request.form.data['matin']
        session['soir']=request.form.data['soir']
        return redirect(url_for('validerSondage'))

@app.route('/sondage/valider', methods=['GET'])
def validerSondage():
    #ajouter les données dans la base de données
    session['sondage']="Merci d'avoir rempli le sondage, celui-ci a bien été enregistré"
    return redirect(url_for('index'))
