from flask import Flask, render_template
import pymysql
from dynaconf import Dynaconf
from flask import request
import flask_login
from flask import flash
from flask import redirect
from flask import abort
app = Flask(__name__)

conf = Dynaconf(
    settings_file = ["settings.toml" ]

)
app = Flask(__name__)
app.secrect_key = conf.secret_key

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view=('/signin')

class User:
    is_authenticated = True
    is_anonymous = False
    is_active = True

    def __init__(self, id, username, email, first_name, last_name):
        self.id = id
        self.username = username
        self.email = email
        self.first_name = first_name
        self. last_name = last_name
    def get_id(self):
        return str(self.id)

@login_manager.user_loader
def load_user(user_id):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM `Customer` WHERE `id` = {user_id};")
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result is not None:
        return User(result["id"], result["username"], result["email"], result["first_name"], result["last_name"])




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
    cursor.execute(f"SELECT * FROM `product` WHERE `id` = {product_id}")
    result = cursor.fetchone()


    if result is None:
        abort(404)

    cursor.execute(f"""

        SELECT `review`,`username`, `review`, `rating` FROM `review` JOIN `customer` ON  WHERE `product_id` = '{product_id}' AND
    
    """)
    review = cursor.fetchall()

    cursor.close
    conn.close
    return render_template("product.html.jinja",product=result, review=review )

@app.route("/product/<product_id>/cart")
@flask_login.login_required
def add_to_cart(product_id):
    conn = connect_db()

    cursor = conn.cursor()
    cursor.execute(f" INSERT INTO `cart` WHERE `id` = {product_id}")
    result = cursor.fetchall()

    cursor.close
    conn.close
    

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
        try:
            cursor.execute(f"""
            INSERT INTO `Customer`
                (`first_name`,`last_name`,`username`,`address`,`email`,`password`,)
                VALUES
                    ( '{first_name}', '{last_name}', '{username}', '{address}', '{email}', '{password}' );
            """)
        except pymysql.err.IntegrityError:
            print("There is someone with that same username in the database ")
            return render_template("sign_up.html.jinja")
        else:
            return redirect("/sign_up")
        finally:
            cursor.close()
            conn.close()
    return render_template
    

@app.route("/signin", methods = ["POST", "GET"])
def sign_in():
    if flask_login.current_user.is_authenticated:
        return redirect("/")
    username = request.form["Username"].strip
    password = request.form["Password"]

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM `Customer` WHERE `username` = '{username}';")

    result = cursor.fetchone()

    if result is None:
        flash("your username/password is incorrect")
    elif password != result["password"]:
        flash("your username/password is incorrect")
    else:
        user = User(result["id"], result["username"], result["email"], result["first_name"], result["last_name"])
        
 
    return render_template("sign_up.html.jinja")

@app.route('/logout')
def logout():
    if flask_login.current_user.is_authenticated:
        return redirect("/")
    flask_login.logout_user()
    return redirect('/')

@app.route('/cart')
@flask_login.login_required
def cart():
    conn = connect_db()
    cursor = conn.cursor()

    customer_id = flask_login.current_user.id
    
    cursor.execute(f"SELECT `name`, `price`, `qty`, `image`, `product_id`, `cart`. `id` FROM `cart` JOIN `product` ON `product_id` = `product`. `id` WHERE `costumer_id` = {customer_id};")

    results = cursor.fetchall()

    cursor.close
    conn.close

    return render_template("cart.html.jinja", products=results)

@app.route("/cart/<cart_id>/add", methods=["POST"])
@flask_login.login_required 
def move_to_cart(product_id):
    qty = request.form['qty']
    customer_id = flask_login.current_user.id

    conn = connect_db()
    cursor = conn.cursor()

    
    cursor.execute(f"INSERT INTO `cart` (`product_id`, `costumer_id`, `qty`) VALUES ({product_id}, {customer_id}, {qty}) ")


    cursor.close
    conn.close

    return redirect("/cart")


@app.route("/cart/<acrt_id>/del", methods=["POST"])
@flask_login.login_required 
def delete_cart(cart_id):

    conn = connect_db()
    cursor = conn.cursor()

    
    cursor.execute(f"DELETE FROM `cart` WHERE `id` = {cart_id} ;")

    results = cursor.fetchall()

    cursor.close
    conn.close

    return redirect("/cart")


@app.route("/cart/<acrt_id>/update", methods=["POST", "GET"])
@flask_login.login_required 
def update_cart(cart_id):

    conn = connect_db()
    cursor = conn.cursor()

    qty=request.form['qty']

    
    cursor.execute(f"UPDATE `cart` SET `qty` = {qty} WHERE `id` = {cart_id} ;")

    results = cursor.fetchall()

    cursor.close
    conn.close


    return redirect("/cart")

@app.route('/checkout', methods=["POST","GET"])
@flask_login.login_required
def checkout():
    conn = connect_db()
    cursor = conn.cursor()
    
    cursor.execute(f'SELECT * FROM `cart`')

    cart = cursor.fetchall()

    cursor.execute(f""" 
        INSERT INTO `sale` (`costumer_id`, `status`)
        VALUES ('{customer_id}', 'pending')
    
    """)

    for product in cart:

        cursor.execute(f""" 
        INSERT INTO `sale_product` (`sale_id`, `product_id`, `qty`)
        VALUES ('{cursor.lastrowid}', '{product['product_id']}', '{product['qty']}')
        """)


    cursor.close
    conn.close

    return redirect('/cart')
