from datetime import datetime
from flask import Blueprint, request, url_for, redirect, render_template, session

from apps.sondage.models import Formulaire
from database.database import doSqlWithEffect, replaceNoneForSQL, getVilles, doSqlWithoutEffect

sondage = Blueprint('sondage', __name__, template_folder="templates", static_folder="static")



@sondage.route("", methods=["POST", "GET"])
def index():
    if session.permanent is False:
        return redirect(url_for('main.inscription'))
    if request.method == "GET" or request.method == "POST":
        form = Formulaire()
        print(form.alimentsMatin)
        return render_template('sondage.html', form=form)
    return redirect(url_for('main.inscription'))

@sondage.route('/verifier', methods=['POST'])
def verifierSondage():
    if session.permanent is False :
        return redirect(url_for('sondage.index'))
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

        return redirect(url_for('sondage.validerSondage'))

@sondage.route('/valider', methods=['GET'])
def validerSondage():
    #ajouter les données dans la base de données
    command = f"INSERT INTO Personne (nom, prenom, age, ville, mail, IDStatutScolaire) VALUES ('{session['nom']}', '{session['prenom']}', {session['age']}, \"{session['ville']}\", '{session['mail']}', {session['niveau']})"
    print("étape 1 ",command)
    if doSqlWithEffect(command) is False:
        return redirect(url_for('sondage.index'))
    print("étape 2")
    command = f"SELECT id FROM Personne WHERE nom = '{session['nom']}' AND prenom = '{session['prenom']}' AND age = {session['age']} AND ville = \"{session['ville']}\" AND mail = '{session['mail']}' AND IDStatutScolaire = {session['niveau']}"
    idPersonne= doSqlWithoutEffect(command)
    print("étape 3 ", session['nom'])
    if idPersonne is False:
        return redirect(url_for('sondage.index'))
    print("étape 4")
    idPersonne = idPersonne[0][0]
    command = f"INSERT INTO Sondage (idPersonne, date, alimentMatin1, alimentMatin2, alimentMatin3, alimentMatin4, alimentMatin5, alimentSoir1, alimentSoir2, alimentSoir3, alimentSoir4, alimentSoir5) VALUES ({idPersonne}, '{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}'" \
              f", {replaceNoneForSQL(session['matin'][0])}, {replaceNoneForSQL(session['matin'][1])}, {replaceNoneForSQL(session['matin'][2])}, {replaceNoneForSQL(session['matin'][3])}, {replaceNoneForSQL(session['matin'][4])}" \
              f", {replaceNoneForSQL(session['soir'][0])}, {replaceNoneForSQL(session['soir'][1])}, {replaceNoneForSQL(session['soir'][2])}, {replaceNoneForSQL(session['soir'][3])}, {replaceNoneForSQL(session['soir'][4])})"

    print(command)
    if doSqlWithEffect(command) is False:
        return redirect(url_for('sondage.index'))
    session['sondage']="Merci d'avoir rempli le sondage, celui-ci a bien été enregistré"
    session['formulaire_soumis'] = True
    return redirect(url_for('main.index'))


@sondage.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

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

    return len(form.errors) == 0