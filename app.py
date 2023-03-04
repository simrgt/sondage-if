import json
from datetime import timedelta

import mysql.connector
import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from flask_wtf import FlaskForm
from wtforms import SelectField, validators, StringField, IntegerField
from datetime import datetime

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

def getVilles():
    uri = "https://geo.api.gouv.fr/communes"
    try:
        uResponse = requests.get(uri)
    except requests.ConnectionError:
        return "Connection Error"
    Jresponse = uResponse.text
    data = json.loads(Jresponse)
    villes = []
    for i in data:
        villes.append((i['nom'], i['nom']))
    return villes
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
    except mysql.connector.errors.ProgrammingError as e:
        print("erreur : ", e)
        return False,e
    except mysql.connector.errors.IntegrityError as e:
        print("erreur : ", e)
        return False,e
    except mysql.connector.Error as e:
        if e.msg == "Too many connections":
            print("erreur : ", e)
            return doSql(sql)
        print("erreur : ", e)
        return False,e
    return result

class FormAliment(FlaskForm):
    groupe = SelectField("groupe", choices=[("Non Selectionné","Non Selectionné")]+doSql(f"SELECT alim_grp_code, alim_grp_nom_fr FROM GroupeAliment"))
    sous_groupe = SelectField("sous_groupe")
    sous_sous_groupe = SelectField("sous_sous_groupe")
    aliment = SelectField("aliment")

    def __init__(self, type, i, *args, **kwargs):
        super(FormAliment, self).__init__(*args, **kwargs)
        self.groupe.name = "groupe_" + str(type) + str(i)
        self.sous_groupe.name = "sous_groupe_" + str(type) + str(i)
        self.sous_sous_groupe.name = "sous_sous_groupe_" + str(type) + str(i)
        self.aliment.name = "aliment_" + str(type) + str(i)
class Formulaire(FlaskForm):
    ages = IntegerField(label="Entrez votre âge (10-18 ans)", id="age", name="age", validators=[validators.InputRequired(message="Veuillez renseigner votre âge"), validators.NumberRange(min=10, max=18, message="Vous devez avoir entre 10 et 18 ans")])
    ville = SelectField("Entrez une ville", choices=[("","")], validators=[validators.InputRequired(message="Veuillez renseigner votre ville")])
    niveau = SelectField("Niveau d'étude", choices=[("","")]+doSql("SELECT IDStatutSColaire, NiveauScolaire FROM StatutScolaire"), validators=[validators.InputRequired(message="Veuillez renseigner votre niveau d'étude")])
    alimentsMatin = []
    alimentsSoir = []
    def __init__(self, *args, **kwargs):
        super(Formulaire, self).__init__(*args, **kwargs)
        self.ville.choices += getVilles()
        #groupeAliment =
        for i in range(5):
            self.alimentsMatin.append(FormAliment("matin", i))
            self.alimentsSoir.append(FormAliment("soir", i))


    def personnaliser(self,s,i):
        self.groupe.name = "groupe_" + str(s) + str(i)
        self.sous_groupe.name = "sous_groupe_" + str(s) + str(i)
        self.sous_sous_groupe.name = "sous_groupe_" + str(s) + str(i)
        self.aliment.name = "aliment_" + str(s) + str(i)
        return self

@app.route("/", methods=['GET', 'POST'])
def index():
    doSql("SELECT * FROM Personne")
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
        #niveaux.name = "statut"
        form = Formulaire()
        if request.args.get("values") != None:
            return render_template("sondage.html", villes=villes, niveaux=niveaux, formMatin=formMatin, formSoir=formSoir)
        else:
            return render_template("sondage.html", form=form, values=None)
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

    form_ville = form.get('ville')
    villes = getVilles()
    if (form_ville,form_ville) not in villes:
        form.errors['ville'] = "Vous devez renseigner une ville valide"
    else:
        form.data['ville'] = form_ville

    for i in form.keys():
        print(i, form.get(i))
    form_niveau = form.get('niveau')
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
    for i in form.errors:
        print(i)
    return len(form.errors) == 0


@app.route('/sondage/verifier', methods=['POST'])
def verifierSondage():
    if session.permanent is False :
        return redirect(url_for('inscription'))
    if request.method == "POST":
        if not validate_sondage_form(request.form):
            return redirect(url_for('sondage'))
        session['ville']=request.form.data['ville']
        session['age']=request.form.data['age']
        session['niveau']=request.form.data['niveau']
        # remplir les données de la session matin et soir avec les données du formulaire (request.form) et mettre vide pour les aliments non renseignés (None) pour avoir une liste de 5 éléments
        session['matin'] = request.form.data['matin']
        for i in range(len(session['matin']),5):
            session['matin'].append(None)
        print(session['matin'])
        session['soir'] = request.form.data['soir']
        for i in range(len(session['soir']),5):
            session['soir'].append(None)
        print(session['soir'])

        return redirect(url_for('validerSondage'))

@app.route('/sondage/valider', methods=['GET'])
def validerSondage():
    #ajouter les données dans la base de données
    command = f"INSERT INTO Personne (nom, prenom, age, ville, mail, IDStatutScolaire) VALUES ('{session['nom']}', '{session['prenom']}', {session['age']}, \"{session['ville']}\", '{session['mail']}', {session['niveau']})"
    if doSql(command) is False:
        return redirect(url_for('inscription'))
    command = f"SELECT id FROM Personne WHERE nom = '{session['nom']}' AND prenom = '{session['prenom']}' AND age = {session['age']} AND ville = \"{session['ville']}\" AND mail = '{session['mail']}' AND IDStatutScolaire = {session['niveau']}"
    idPersonne = doSql(command)
    if idPersonne is False:
        return redirect(url_for('inscription'))
    idPersonne = idPersonne[0][0]
    command = f"INSERT INTO Sondage (idPersonne, date, alimentMatin1, alimentMatin2, alimentMatin3, alimentMatin4, alimentMatin5, alimentSoir1, alimentSoir2, alimentSoir3, alimentSoir4, alimentSoir5) VALUES ({idPersonne}, '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'" \
              f", {replaceNoneForSQL(session['matin'][0])}, {replaceNoneForSQL(session['matin'][1])}, {replaceNoneForSQL(session['matin'][2])}, {replaceNoneForSQL(session['matin'][3])}, {replaceNoneForSQL(session['matin'][4])}" \
              f", {replaceNoneForSQL(session['soir'][0])}, {replaceNoneForSQL(session['soir'][1])}, {replaceNoneForSQL(session['soir'][2])}, {replaceNoneForSQL(session['soir'][3])}, {replaceNoneForSQL(session['soir'][4])})"

    print(command)
    if doSql(command) is False:
        return redirect(url_for('inscription'))
    session['sondage']="Merci d'avoir rempli le sondage, celui-ci a bien été enregistré"
    return redirect(url_for('index'))


def replaceNoneForSQL(value):
    if value is None:
        return "NULL"
    else:
        return value