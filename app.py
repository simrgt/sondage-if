
# A very simple Flask Hello World app for you to get started with...

from flask import Flask, render_template
import mysql.connector

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config["DEBUG"] = True
# app.config['MYSQL_HOST'] = 'bqpjqiutmrlk6tkmm9ef-mysql.services.clever-cloud.com'
# app.config['MYSQL_USER'] = 'usfyvwadlczjc1jj'
# app.config['MYSQL_PASSWORD'] = 'Jq2Sn2xCIZnqlEOZL1E4'
# app.config['MYSQL_DB'] = 'bqpjqiutmrlk6tkmm9ef'

# mysql = MySQL(app)


@app.route("/")
def index():
    db = mysql.connector.connect(
        host="bqpjqiutmrlk6tkmm9ef-mysql.services.clever-cloud.com",
        user="usfyvwadlczjc1jj",
        password="Jq2Sn2xCIZnqlEOZL1E4",
        database="bqpjqiutmrlk6tkmm9ef"
    )
    c= db.cursor()
    c.execute('''INSERT INTO Personne VALUES(6)''')
    db.commit()

    db.close()
    # # Creating a connection cursor
    # cursor = mysql.connection.cursor()
    #
    # # Executing SQL Statements
    # cursor.execute(''' INSERT INTO Personne VALUES(1,"simon","regenwetter",19,"Draveil","sim@gmail.com") ''')
    #
    # # Saving the Actions performed on the DB
    # mysql.connection.commit()
    #
    # # Closing the cursor
    # cursor.close()
    return render_template("index.html")

@app.route('/', subdomain ='app')
def practice():
    return "salut"
