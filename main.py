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


@app.route("/product/<product_id>")
def product_page(product_id):
    conn = connect_db()

    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM `Product` WHERE `id` = {product_id}")
    result = cursor.fetchone()

    cursor.close
    conn.close


    return product_id

@app.route("/sign_up", methods=["POST","GET"])
def sign_up():
    if request.method == 'POST':
        first_name = request.form["First_name"]
        last_name = request.form["Last_name"]
        username = request.form["Username"]
        address = request.form["address"]
        email = request.form["Email"]
        password = request.form["Password"]
    
        conn = connect_db()

        cursor = conn.cursor()

        cursor.execute(f"""
        INSERT INTO `Customer`
            (`first_name`,`last_name`,`username`,`address`,`email`,`password`,)
            VALUES
                ( '{first_name}', '{last_name}', '{username}', '{address}', '{email}', '{password}' );
        """)
        return redirect("/signin")
    return render_template("sign_up.html.jinja")