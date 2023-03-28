import json
import sqlite3

import mysql.connector
import requests

from config import DATABASE


def doSQLAdmin(sql,tuple):
    conn = sqlite3.connect(DATABASE)
    cur = conn.execute(sql, tuple)
    rv = cur.fetchall()
    cur.close()
    return rv


configDB = {
    'host':"bqpjqiutmrlk6tkmm9ef-mysql.services.clever-cloud.com",
    'user':"usfyvwadlczjc1jj",
    'password':"Jq2Sn2xCIZnqlEOZL1E4",
    'database':"bqpjqiutmrlk6tkmm9ef"
}
def doSqlWithEffect(sql):
    try :
        db1 = mysql.connector.connect(pool_name="mypool", pool_size=1, **configDB)
        c = db1.cursor()
        c.execute(sql)
        c.close()
        db1.commit()
        db1.close()
    except mysql.connector.errors.ProgrammingError as e:
        print("erreur : ", e)
        return False
    except mysql.connector.errors.IntegrityError as e:
        print("erreur : ", e)
        return False
    except mysql.connector.Error as e:
        if e.msg == "Too many connections":
            print("erreur : ", e)
            return doSqlWithEffect(sql)
        print("erreur : ", e)
        return False
    return True

def doSqlWithoutEffect(sql):
    try :
        db1 = mysql.connector.connect(pool_name="mypool", pool_size=1, **configDB)
        c = db1.cursor()
        c.execute(sql)
        result = c.fetchall()
        c.close()
        db1.commit()
        db1.close()
    except mysql.connector.errors.ProgrammingError as e:
        print("erreur : ", e)
        return False
    except mysql.connector.errors.IntegrityError as e:
        print("erreur : ", e)
        return False
    except mysql.connector.Error as e:
        if e.msg == "Too many connections":
            print("erreur : ", e)
            return doSqlWithoutEffect(sql)
        print("erreur : ", e)
        return False
    return result

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

def replaceNoneForSQL(value):
    if value is None:
        return "NULL"
    else:
        return value


def getDatabase():
    database = {}
    try:
        db1 = mysql.connector.connect(pool_name="mypool", pool_size=1, **configDB)
        c = db1.cursor()

        tables = ['Sondage', 'Personne', 'Aliment', 'GroupeAliment',
                  'SousGroupeAliment', 'SousSousGroupeAliment', 'StatutScolaire']

        for table in tables:
            c.execute(f"SELECT * FROM {table}")
            columns = c.column_names
            rows = list(c.fetchall())
            table_dict = {}
            for col in columns:
                col_values = [row[columns.index(col)] for row in rows]
                table_dict[col] = col_values
            database[table] = table_dict

        c.close()
        db1.commit()
        db1.close()
    except mysql.connector.errors.ProgrammingError as e:
        print("erreur : ", e)
        return False
    except mysql.connector.errors.IntegrityError as e:
        print("erreur : ", e)
        return False
    except mysql.connector.Error as e:
        if e.msg == "Too many connections":
            print("erreur : ", e)
            return getDatabase()
        print("erreur : ", e)
        return False
    return database
