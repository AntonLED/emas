import mysql.connector
from mas.transactions.database_commands import Database_commands


database_params = {
    "host": "192.168.50.104",
    "port": 3306,
    "database": "Database1",
    "user": "localuser",
    "password": "miptlocal",
}

try:
    database = mysql.connector.connect(
        host=database_params["host"],
        port=database_params["port"],
        database=database_params["database"],
        user=database_params["user"],
        password=database_params["password"],
    )
except mysql.connector.Error as err:
    print(err.__str__())
