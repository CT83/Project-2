import os
import subprocess
import tempfile
from pathlib import Path
from shutil import copyfileobj

from flask import Flask, flash, redirect, render_template, request, send_file, url_for
from flask_bootstrap import Bootstrap
from flask_restful import Api
from flask_wtf import FlaskForm
from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import reflection
from sqlalchemy.engine.url import make_url
from sqlalchemy_schemadisplay import create_schema_graph
from wtforms import StringField

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
        engine = create_engine(db_url, echo=False)
        app.config["db_type"] = engine.url.drivername
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
    write_history(query)
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
            result += str(index)
    if result == "":
        result = "No indices"
    return render_template("home.html", result=result)


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


@app.route("/backup", methods=["GET"])
def backup():
    print("Type of database - ", app.config["db_type"])
    f = open("backup.db", "w")
    if app.config["db_type"] == "postgres":
        subprocess.call(["pg_dump", app.config["db_url"]], stdout=f)
    elif app.config["db_type"] == "mysql":
        # mysqldump -u admin -pmysql testDB > backup.db
        url = make_url(app.config["db_url"])
        print("in")
        # print(subprocess.check_output(["mysqldump", "-u" + url.username, "-p" + url.password, url.database]))
        subprocess.call(
            ["mysqldump", "-u" + url.username, "-p" + url.password, url.database],
            stdout=f,
            shell=True,
        )
    else:
        url = make_url(app.config["db_url"])
        return send_file(url.database)
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

    # mysql db_name < backup-file.sql
    # psql -U username -d dbname < filename.sql

    f = open(file_path)
    engine = create_engine(app.config["db_url"], echo=False)

    if app.config["db_type"] == "postgres":
        engine.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        subprocess.call(["psql", app.config["db_url"]], stdin=f)
    elif app.config["db_type"] == "mysql":
        # mysqldump db_name > backup-file.sql
        url = make_url(app.config["db_url"])

        subprocess.call(
            ["mysql", "-u" + url.username, "-p" + url.password, url.database], stdin=f
        )
    else:
        print(file_path)
        url = make_url(app.config["db_url"])
        f = open(file_path, "rb")
        print(url.database)
        db_file = open(url.database, "wb")
        print(db_file)
        copyfileobj(f, db_file)
        f.close()
        db_file.close()

    flash("Restored database succesfully")
    return redirect(url_for("home"))


def history_file_absolute_path():
    history_filename = ".adm.history"
    return os.path.join(os.path.expanduser("~"), history_filename)


def get_history():
    history_file_path = history_file_absolute_path()

    if not os.path.exists(history_file_path):
        return []

    with open(history_file_path, encoding="utf-8") as file:
        data = file.read()
        return data.split("br\n")


@app.route("/history", methods=["GET"])
def history():
    data = get_history()
    return {"history": data}


def write_history(text):
    history_file_path = history_file_absolute_path()

    with open(history_file_path, "a", encoding="utf-8") as file:
        file.write(text + "br\n")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
