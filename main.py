from flask import Flask, render_template
import pymysql
from dynaconf import Dynaconf
from flask import request
app = Flask(__name__)

conf = Dynaconf(
    settings_file = ["settings.toml" ]
)

def connect_db():
    conn = pymysql.connect(
        host = "10.100.34.80",
        database = "calleyne_the_mix",
        user = "calleyne",
        password = conf.password,
        autocommit = True,
        cursorclass = pymysql.cursors.DictCursor
    )
    return conn
@app.route("/")
def index():
    return render_template("homepage.html.jinja")

@app.route("/browse")
def product_browse():
    query = request.args.get('query')
    conn = connect_db()

    cursor = conn.cursor()
    if query is None:
        cursor.execute("SELECT * FROM `product`;")
    else:
        cursor.execute(f"SELECT * FROM `product` WHERE `name` LIKE '%{query}%';")

    results = cursor.fetchall()

    cursor.close
    conn.close


    return render_template("browse.html.jinja", products = results)