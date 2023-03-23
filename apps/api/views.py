from flask import Blueprint, render_template, jsonify

from database.database import doSqlWithoutEffect

api = Blueprint('api', __name__, template_folder="templates")

@api.route('/sousGroupe/<groupe>')
def sousGroupe(groupe):
    sous_groupes = doSqlWithoutEffect(f"SELECT alim_ssgrp_code ,alim_ssgrp_nom_fr FROM SousGroupeAliment WHERE idGroupeAliment ={groupe}")
    sous_groupesArray = []
    for sous_groupe in sous_groupes:
        ssGrp = {}
        ssGrp['id'] = sous_groupe[0]
        ssGrp['name'] = sous_groupe[1]
        sous_groupesArray.append(ssGrp)

    return jsonify({'sousGroupe':sous_groupesArray})

@api.route('/sousSousGroupe/<sousGroupe>')
def sousSousGroupe(sousGroupe):
    sous_sous_groupes = doSqlWithoutEffect(f"SELECT alim_ssssgrp_code ,alim_ssssgrp_nom_fr FROM SousSousGroupeAliment WHERE alim_ssgrp_code ={sousGroupe}")

    sous_sous_groupesArray = []
    for sous_sous_groupe in sous_sous_groupes:
        ssssGrp = {}
        ssssGrp['id'] = sous_sous_groupe[0]
        ssssGrp['name'] = sous_sous_groupe[1]
        sous_sous_groupesArray.append(ssssGrp)

    return jsonify({'sousSousGroupe':sous_sous_groupesArray})

@api.route('/aliment/<sousSousGroupe>')
def aliment(sousSousGroupe):

    sous_sous_groupes = doSqlWithoutEffect(f"SELECT alim_code ,alim_nom_fr FROM Aliment WHERE alim_ssssgrp_code ={sousSousGroupe}")

    sous_sous_groupesArray = []
    for sous_sous_groupe in sous_sous_groupes:
        ssssGrp = {}
        ssssGrp['id'] = sous_sous_groupe[0]
        ssssGrp['name'] = sous_sous_groupe[1]
        sous_sous_groupesArray.append(ssssGrp)

    return jsonify({'aliment':sous_sous_groupesArray})

@api.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404