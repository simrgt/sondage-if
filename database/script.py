import random
import time
from datetime import datetime, timedelta

import mysql.connector

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

def randomDate():
    # Définir les dates de début et de fin
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 3, 25)

    # Calculer la différence de temps entre les deux dates en secondes
    time_diff = (end_date - start_date).total_seconds()

    # Générer un nombre aléatoire de secondes entre les deux dates
    random_seconds = random.randrange(time_diff)

    # Ajouter le nombre de secondes aléatoire à la date de début pour obtenir une date aléatoire
    random_date = start_date + timedelta(seconds=random_seconds)
    return random_date.strftime("%Y-%m-%d")

def insertSondage(id,aliments):
    time.sleep(0.4)
    doSqlWithEffect(f"INSERT INTO Sondage (date, idPersonne, alimentMatin1, alimentMatin2, alimentMatin3, alimentMatin4, alimentMatin5, alimentSoir1, alimentSoir2, alimentSoir3, alimentSoir4, alimentSoir5) VALUES ('{randomDate()}', {id}, {aliments[0]}, {aliments[1]}, {aliments[2]}, {aliments[3]}, {aliments[4]}, {aliments[5]}, {aliments[6]}, {aliments[7]}, {aliments[8]}, {aliments[9]})")

def modifySondage():
    aliment = doSqlWithoutEffect("SELECT alim_code FROM Aliment")
    aliments = []
    for alim in aliment:
        aliments.append(alim[0])
    for i in range(88-32):
        insertSondage(i+50,aliments)

if __name__ == '__main__':
    modifySondage()



