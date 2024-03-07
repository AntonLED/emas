import mysql.connector

cnx = mysql.connector.connect(user="root", password="test",
                              host="localhost")
cnx.close()