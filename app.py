from flask import Flask
from flask_login import LoginManager

from apps.analyse.models import User
from apps.analyse.views import analyse
# blueprint import
from apps.main.views import main
from apps.sondage.views import sondage
from apps.api.views import api
from database.database import doSQLAdmin


app = Flask(__name__)
# setup with the configuration provided
app.config.from_object('config.DevelopmentConfig')

# register blueprint
app.register_blueprint(main)
app.register_blueprint(sondage, url_prefix="/sondage")
app.register_blueprint(analyse, url_prefix="/analyse")
app.register_blueprint(api, url_prefix="/api")

# setup login manager
login_manager = LoginManager()
login_manager.login_view = 'analyse.login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    rv = doSQLAdmin("SELECT * FROM user WHERE id = ?", (user_id,))
    return User(rv[0][0], rv[0][1], rv[0][2]) if rv else None



