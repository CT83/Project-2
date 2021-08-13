import os

from flask import Flask, render_template, request, jsonify
from flask_restful import Api, Resource

from extensions import db
from utils import get_connector_for_database

app = Flask(__name__, template_folder="templates")
api = Api(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DATABASE_URL"]
db.init_app(app)


class Database(db.Model):
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(200), unique=False, nullable=True)
    port = db.Column(db.Integer)
    database = db.Column(db.String(200), unique=False, nullable=True)
    user = db.Column(db.String(200), unique=False, nullable=True)
    password = db.Column(db.String(200), unique=False, nullable=True)
    db_type = db.Column(db.String(200), unique=False, nullable=True)


class ListTablesDatabaseRes(Resource):

    def get(self):
        return {'hello': 'world'}


class SelectAllTableDatabaseRes(Resource):

    def post(self):
        data = request.get_json(force=True)
        db_id = data["db_id"]
        table_name = data["table_name"]
        connector = get_connector_for_database(db_id=db_id, )
        rows = connector.select_all(table_name=table_name)
        return jsonify(rows)


class ServerRes(Resource):

    def get(self):
        return {'hello': 'world'}

    def post(self):
        data = request.get_json(force=True)
        host = data["host"]
        port = data["port"]
        database = data["database"]
        user = data["user"]
        password = data["password"]
        db_type = data["db_type"]

        db_instance = Database(host=host, port=port, database=database, user=user, password=password, db_type=db_type)
        db.session.add(db_instance)
        db.session.commit()
        return jsonify({"id": db_instance.id})


@app.route("/home")
def home():
    return render_template("home.html", text="text")


api.add_resource(ServerRes, '/servers')
api.add_resource(SelectAllTableDatabaseRes, '/select-all')

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
