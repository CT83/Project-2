from concurrent.futures.process import _ResultItem
import os

from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_bootstrap import Bootstrap
from flask_restful import Api, Resource
from flask_wtf import FlaskForm
from sqlalchemy import create_engine
from sqlalchemy.engine import reflection, result
from wtforms import StringField

from extensions import db
from utils import get_connector_for_database

app = Flask(__name__, template_folder="templates")
api = Api(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
app.config["SECRET_KEY"] = "secret"
app.config["db_url"] = ""
db.init_app(app)

bootstrap = Bootstrap(app)


class Database(db.Model):
    __table_args__ = {"extend_existing": True}
    id = db.Column(db.Integer, primary_key=True)
    host = db.Column(db.String(200), unique=False, nullable=True)
    port = db.Column(db.Integer)
    database = db.Column(db.String(200), unique=False, nullable=True)
    user = db.Column(db.String(200), unique=False, nullable=True)
    password = db.Column(db.String(200), unique=False, nullable=True)
    db_type = db.Column(db.String(200), unique=False, nullable=True)


class ListTablesDatabaseRes(Resource):
    def get(self):
        return {"hello": "world"}


class SelectAllTableDatabaseRes(Resource):
    def post(self):
        data = request.get_json(force=True)
        db_id = data["db_id"]
        table_name = data["table_name"]
        connector = get_connector_for_database(
            db_id=db_id,
        )
        rows = connector.select_all(table_name=table_name)
        return jsonify(rows)


class ServerRes(Resource):
    def get(self):
        return {"hello": "world"}

    def post(self):
        data = request.get_json(force=True)
        host = data["host"]
        port = data["port"]
        database = data["database"]
        user = data["user"]
        password = data["password"]
        db_type = data["db_type"]

        db_instance = Database(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            db_type=db_type,
        )
        db.session.add(db_instance)
        db.session.commit()
        return jsonify({"id": db_instance.id})


@app.route("/")
def home():
    return render_template("home.html")


class ConnectForm(FlaskForm):
    db_url = StringField("Database URL")


@app.route("/connect", methods=["GET", "POST"])
def connect():
    form = ConnectForm()
    if form.validate_on_submit():
        db_url = form.db_url.data
        app.config["db_url"] = db_url
        engine = create_engine(db_url, echo=False)
        return redirect(url_for("home"))

    # db_url = request.args.get("url")
    # app.config["db_url"] = db_url
    # engine = create_engine(db_url, echo=False)

    return render_template("connect.html", form=form)


@app.route("/list_tables", methods=["GET"])
def list_tables():
    engine = create_engine(app.config["db_url"], echo=False)
    result = engine.table_names()
    return render_template("home.html", result = result)

class ExecuteForm(FlaskForm):
    db_url = StringField("")


@app.route("/execute", methods=["POST"])
def execute():
    query = request.form.get("query")
    engine = create_engine(app.config["db_url"], echo=False)
    result = engine.execute(query)

    try:
        rows = ""

        for row in result:
            rows += str(row) + '\n'

        return redirect(url_for("output", result = rows, query = query))
    except:
        return redirect(url_for("home"))

@app.route("/output", methods=["GET", "POST"])
def output():
    result = request.args['result']
    query = request.args['query']
    return render_template("home.html", result = result, query = query)



@app.route("/list_indices", methods=["GET"])
def indices():
    engine = create_engine(app.config["db_url"], echo=False)
    insp = reflection.Inspector.from_engine(engine)
    result = ""
    for name in insp.get_table_names():
        for index in insp.get_indexes(name):
            result += index
    if result == "":
        result = "No indices"
    return render_template("home.html", result = result)

from sqlalchemy_schemadisplay import create_schema_graph
from sqlalchemy import MetaData

@app.route("/er", methods=["GET"])
def er():
    engine = create_engine(app.config["db_url"], echo=False)
    graph = create_schema_graph(metadata=MetaData(app.config["db_url"]),
        show_datatypes=False,
        show_indexes=False,
        rankdir='LR',
        concentrate=False
    )
    graph.write_png('static/er.png') # write out the file
    return render_template("er.html")



api.add_resource(ServerRes, "/servers")
api.add_resource(SelectAllTableDatabaseRes, "/select-all")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
