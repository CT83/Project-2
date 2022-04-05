import os

from flask import (
    Flask,
    redirect,
    render_template,
    request,
    url_for,
    send_file,
    flash,
)
from flask_bootstrap import Bootstrap
from flask_restful import Api
from flask_wtf import FlaskForm
from sqlalchemy import create_engine
from sqlalchemy.engine import reflection
from wtforms import StringField
from pathlib import Path
import tempfile
from sqlalchemy import MetaData
from shutil import copyfileobj

from extensions import db

app = Flask(__name__, template_folder="templates")
api = Api(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")

app.config["SECRET_KEY"] = "secret"
app.config["db_url"] = os.environ.get("DATABASE_URL")
SQLALCHEMY_TRACK_MODIFICATIONS = False
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = SQLALCHEMY_TRACK_MODIFICATIONS
app.config["UPLOAD_FOLDER"] = tempfile.mkdtemp()
app.config["db_type"] = "postgres"
db.init_app(app)
bootstrap = Bootstrap(app)


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
        print(db_url)
        engine = create_engine(db_url, echo=False)
        app.config["db_type"] = engine.url.database
        print(app.config["db_type"])
        return redirect(url_for("home"))

    # db_url = request.args.get("url")
    # app.config["db_url"] = db_url
    # engine = create_engine(db_url, echo=False)

    return render_template("connect.html", form=form)


@app.route("/list_tables", methods=["GET"])
def list_tables():
    engine = create_engine(app.config["db_url"], echo=False)
    result = engine.table_names()
    result = "Table count - " + str(len(result)) + "\n" + str(result)
    return render_template("home.html", result=result)


class ExecuteForm(FlaskForm):
    db_url = StringField("")


@app.route("/execute", methods=["POST"])
def execute():
    query = request.form.get("query")
    engine = create_engine(app.config["db_url"], echo=False)

    try:
        result = engine.execute(query)
        rows = ""

        for row in result:
            rows += str(row) + "\n"

        return redirect(url_for("output", result=rows, query=query))
    except:
        return redirect(url_for("home"))


@app.route("/output", methods=["GET", "POST"])
def output():
    result = request.args["result"]
    query = request.args["query"]
    return render_template("home.html", result=result, query=query)


@app.route("/list_indices", methods=["GET"])
def indices():
    engine = create_engine(app.config["db_url"], echo=False)
    insp = reflection.Inspector.from_engine(engine)
    result = ""
    for name in insp.get_table_names():
        for index in insp.get_indexes(name):
            print(type(index))
            result += str(index)
    if result == "":
        result = "No indices"
    return render_template("home.html", result=result)


from sqlalchemy_schemadisplay import create_schema_graph
from sqlalchemy import MetaData


@app.route("/er", methods=["GET"])
def er():
    engine = create_engine(app.config["db_url"], echo=False)
    graph = create_schema_graph(
        metadata=MetaData(app.config["db_url"]),
        show_datatypes=True,
        show_indexes=True,
        rankdir="LR",
        concentrate=False,
    )
    graph.write_png("static/er.png")  # write out the file
    return render_template("er.html")


import subprocess


@app.route("/backup", methods=["GET"])
def backup():
    print("Type of database - ", app.config["db_type"])
    f = open("backup.db", "w")
    if app.config["db_type"] == "postgres":
        subprocess.call(["pg_dump", app.config["db_url"]], stdout=f)
    if app.config["db_type"] == "mysql":
        # mysqldump db_name > backup-file.sql
        subprocess.call(["mysqldump", app.config["db_url"]], stdout=f)
    if app.config["db_type"] == "sqlite":
        return send_file(app.config["db_url"])
    return send_file(f.name)


@app.route("/restore", methods=["GET", "POST"])
def restore():

    if request.method == "GET":
        return render_template("restore.html")
    file = request.files["myfile"]

    if file.filename == "":
        flash("No selected file")
        return redirect(request.url)
    if file:
        filename = file.filename
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        restore_from_file(file)

        return redirect(url_for("home"))
    return redirect(url_for("home"))


def restore_from_file(file):
    file_path = Path(app.config["UPLOAD_FOLDER"]) / file.filename
    print("file path ", file_path)

    # mysql db_name < backup-file.sql
    # psql -U username -d dbname < filename.sql

    f = open(file_path)
    engine = create_engine(app.config["db_url"], echo=False)

    if app.config["db_type"] == "postgres":
        engine.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        subprocess.call(["psql", app.config["db_url"]], stdin=f)
    elif app.config["db_type"] == "mysql":
        # mysqldump db_name > backup-file.sql
        subprocess.call(["mysql", app.config["db_url"]], stdin=f)
    else:
        f = open(file_path, "rb")
        # open connected db file
        db_file = open(app.config["db_type"], "wb")
        # open backup file
        copyfileobj(f, db_file)

    flash("Restored database succesfully")
    return redirect(url_for("home"))


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
