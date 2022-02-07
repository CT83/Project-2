import mysql.connector
from mysql.connector.cursor import MySQLCursorDict


class MySQLConnector:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.passsword = password

    def select_all(self, table_name):
        try:
            mydb = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.passsword,
                database=self.database,
                port=self.port,
            )
            mycursor = mydb.cursor(dictionary=True)
            mycursor.execute("SELECT * FROM {}".format(table_name))
            rows = mycursor.fetchall()
            return rows
        except (Exception) as error:
            print(error)

    def list_tables(self, table_name):
        pass


if __name__ == "__main__":
    mys = MySQLConnector(
        host="localhost",
        port=3306,
        database="db_admin_db_slave",
        user="root",
        password="somebeach123",
    )
    rows = mys.select_all("animals")
    print(rows)
