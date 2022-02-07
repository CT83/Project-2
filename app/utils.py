from db_connectors.mysql_connector import MySQLConnector
from db_connectors.pg_connector import PostGresConnector


def get_connector_for_database(db_id):
    from app import Database

    database = Database.query.get(db_id)
    if database.db_type == "postgres":
        return PostGresConnector(
            host=database.host,
            port=database.port,
            database=database.database,
            user=database.user,
            password=database.password,
        )
    elif database.db_type == "mysql":
        return MySQLConnector(
            host=database.host,
            port=database.port,
            database=database.database,
            user=database.user,
            password=database.password,
        )
