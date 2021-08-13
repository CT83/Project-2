import psycopg2


class MySQLConnector():

    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.passsword = password

    def select_all(self, table_name):
        try:
            conn = psycopg2.connect(
                host=self.host, port=self.port,
                database=self.database,
                user=self.user,
                password=self.passsword)
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM {}".format(table_name))
            rows = list(cur.fetchall())
            print("The number of parts: ", cur.rowcount)
            for row in rows:
                print(row)

            cur.close()
            return rows
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

    def list_tables(self, table_name):
        pass


if __name__ == "__main__":
    pgc = MySQLConnector(host="localhost", port=5432,
                         database="db_admin_db_slave",
                         user="user",
                         password="hardpassword")
    pgc.select_all("cars")
