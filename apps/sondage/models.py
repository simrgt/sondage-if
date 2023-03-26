from flask_wtf import FlaskForm
from wtforms import IntegerField, SelectField, validators

from database.database import getVilles, doSqlWithoutEffect


class Formulaire(FlaskForm):
    ages = IntegerField(label="Entrez votre âge (10-18 ans)", id="age", name="age", validators=[validators.InputRequired(message="Veuillez renseigner votre âge"), validators.NumberRange(min=10, max=18, message="Vous devez avoir entre 10 et 18 ans")])
    ville = SelectField("Entrez une ville", choices=[("","")], validators=[validators.InputRequired(message="Veuillez renseigner votre ville")])
    niveau = SelectField("Niveau d'étude", choices=[("","")], validators=[validators.InputRequired(message="Veuillez renseigner votre niveau d'étude")])
    alimentsMatin = []
    alimentsSoir = []
    def __init__(self, *args, **kwargs):
        super(Formulaire, self).__init__(*args, **kwargs)
        self.ville.choices += getVilles()
        self.niveau.choices += doSqlWithoutEffect("SELECT IDStatutSColaire, NiveauScolaire FROM StatutScolaire")
        if len(self.alimentsMatin) == 0 and len(self.alimentsSoir) == 0:
            for i in range(5):
                self.alimentsMatin.append(FormAliment("matin", i))
                self.alimentsSoir.append(FormAliment("soir", i))


class FormAliment(FlaskForm):
    groupe = SelectField("groupe", choices=[("Non Selectionné","Non Selectionné")])
    sous_groupe = SelectField("sous_groupe")
    sous_sous_groupe = SelectField("sous_sous_groupe")
    aliment = SelectField("aliment")

    def __init__(self, type, i, *args, **kwargs):
        super(FormAliment, self).__init__(*args, **kwargs)
        self.groupe.name = "groupe_" + str(type) + str(i)
        self.sous_groupe.name = "sous_groupe_" + str(type) + str(i)
        self.sous_sous_groupe.name = "sous_sous_groupe_" + str(type) + str(i)
        self.aliment.name = "aliment_" + str(type) + str(i)
        self.groupe.choices += doSqlWithoutEffect(f"SELECT alim_grp_code, alim_grp_nom_fr FROM GroupeAliment")