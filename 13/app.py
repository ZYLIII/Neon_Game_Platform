from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re

app = Flask(__name__)

app.secret_key = 'xyzsdfg'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '991105'
app.config['MYSQL_DB'] = 'user-system'

mysql = MySQL(app)


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    mesage = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute(
            'SELECT * FROM user WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            session['role'] = user['role']
            if user['role'] == 'admin':
                mesage = 'Admin logged in successfully !'
                return redirect(url_for('users'))
            else:
                mesage = 'Logged in successfully !'
                return redirect(url_for('user_dashboard'))
        else:
            mesage = 'Please enter correct email / password !'
    return render_template('Login-Register.html', mesage=mesage)


@app.route('/user_dashboard')
def user_dashboard():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

        if session.get('role') == 'admin':
            cursor.execute('SELECT * FROM user')
            users = cursor.fetchall()
        else:
            cursor.execute(
                'SELECT * FROM user WHERE userid = % s', (session['userid'],))
            users = [cursor.fetchone()]

        return render_template('user_dashboard.html', users=users)

    return redirect(url_for('Login-Register'))


@app.route('/logout')
@app.route('/register', methods=['GET', 'POST'])
def register():
    mesage = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        userName = request.form['name']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']
        country = request.form['country']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = % s', (email, ))
        account = cursor.fetchone()
        if account:
            mesage = 'User already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            mesage = 'Invalid email address !'
        elif not userName or not password or not email:
            mesage = 'Please fill out the form !'
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s, % s, % s)',
                           (userName, email, password, role, country))
            mysql.connection.commit()
            mesage = 'New user created!'
    elif request.method == 'POST':
        mesage = 'Please fill out the form !'
    return render_template('register.html', mesage=mesage)


@app.route("/users", methods=['GET', 'POST'])
def users():
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user')
        users = cursor.fetchall()
        return render_template("users.html", users=users)
    return redirect(url_for('Login-Register'))


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    msg = ''
    if 'loggedin' in session:
        editUserId = request.args.get('userid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE userid = % s', (editUserId, ))
        editUser = cursor.fetchone()
        if request.method == 'POST' and 'name' in request.form and 'userid' in request.form and 'role' in request.form and 'country' in request.form:
            userName = request.form['name']
            role = request.form['role']
            country = request.form['country']
            userId = request.form['userid']
            if not re.match(r'[A-Za-z0-9]+', userName):
                msg = 'name must contain only characters and numbers !'
            else:
                cursor.execute('UPDATE user SET  name =% s, role =% s, country =% s WHERE userid =% s', (
                    userName, role, country, (userId, ), ))
                mysql.connection.commit()
                msg = 'User updated !'
                return redirect(url_for('users'))
        elif request.method == 'POST':
            msg = 'Please fill out the form !'
        return render_template("edit.html", msg=msg, editUser=editUser)
    return redirect(url_for('Login-Register'))


@app.route("/password_change", methods=['GET', 'POST'])
def password_change():
    mesage = ''
    if 'loggedin' in session:
        changePassUserId = request.args.get('userid')
        if request.method == 'POST' and 'password' in request.form and 'confirm_pass' in request.form and 'userid' in request.form:
            password = request.form['password']
            confirm_pass = request.form['confirm_pass']
            userId = request.form['userid']
            if not password or not confirm_pass:
                mesage = 'Please fill out the form !'
            elif password != confirm_pass:
                mesage = 'Confirm password is not equal!'
            else:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor.execute(
                    'UPDATE user SET  password =% s WHERE userid =% s', (password, (userId, ), ))
                mysql.connection.commit()
                mesage = 'Password updated !'
        elif request.method == 'POST':
            mesage = 'Please fill out the form !'
        return render_template("password_change.html", mesage=mesage, changePassUserId=changePassUserId)
    return redirect(url_for('Login-Register'))


@app.route("/view", methods=['GET', 'POST'])
def view():
    if 'loggedin' in session:
        viewUserId = request.args.get('userid')
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE userid = % s', (viewUserId, ))
        user = cursor.fetchone()
        return render_template("view.html", user=user)
    return redirect(url_for('Login-Register'))


@app.route("/delete/<int:userid>", methods=['POST'])
def delete(userid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM user WHERE userid = % s', (userid, ))
    mysql.connection.commit()

    if session['role'] == 'admin':
        # If the logged-in user is an admin, stay on the users page
        return redirect(url_for('users'))
    else:
        # If it's a regular user, redirect to the login page
        return redirect(url_for('Login-Register'))


@app.route("/")
def index():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Goods ORDER BY views_count DESC LIMIT 2")
    hot_goods = cursor.fetchall()
    cursor.execute(
        "SELECT * FROM Goods WHERE is_new = 1 ORDER BY addtime DESC LIMIT 12")
    new_goods = cursor.fetchall()
    cursor.execute(
        "SELECT * FROM Goods WHERE is_sale = 1 ORDER BY addtime DESC LIMIT 12")
    sale_goods = cursor.fetchall()
    return render_template('xxxx.html', new_goods=new_goods, sale_goods=sale_goods, hot_goods=hot_goods)


@app.route("/goods_list/<int:supercat_id>/")
def goods_list(supercat_id=None):
    page = request.args.get('page', 1, type=int)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM Goods WHERE supercat_id = %s LIMIT 12 OFFSET %s", (supercat_id, (page-1)*12))
    page_data = cursor.fetchall()
    cursor.execute(
        "SELECT * FROM Goods WHERE supercat_id = %s ORDER BY views_count DESC LIMIT 7", (supercat_id,))
    hot_goods = cursor.fetchall()
    return render_template('goods_list.html', page_data=page_data, hot_goods=hot_goods, supercat_id=supercat_id)


# Add the remaining routes using a similar pattern

app = Flask(__name__)
mysql = MySQL(app)


@app.route("/goods_detail/<int:id>/")
def goods_detail(id=None):
    user_id = session.get('user_id', 0)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    cursor.execute("SELECT * FROM Goods WHERE id = %s", (id,))
    goods = cursor.fetchone()

    if not goods:
        return "404: Goods not found", 404

    cursor.execute(
        "UPDATE Goods SET views_count = views_count + 1 WHERE id = %s", (id,))
    mysql.connection.commit()

    cursor.execute(
        "SELECT * FROM Goods WHERE subcat_id = %s ORDER BY views_count DESC LIMIT 5", (goods['subcat_id'],))
    hot_goods = cursor.fetchall()

    cursor.execute(
        "SELECT * FROM Goods WHERE subcat_id = %s ORDER BY addtime DESC LIMIT 5", (goods['subcat_id'],))
    similar_goods = cursor.fetchall()

    cursor.execute(
        "SELECT COUNT(*) FROM Collect WHERE user_id = %s AND goods_id = %s", (user_id, id))
    is_collect = cursor.fetchone()['COUNT(*)']

    return render_template('goods_detail.html', goods=goods, hot_goods=hot_goods, similar_goods=similar_goods,
                           user_id=user_id, is_collect=is_collect)


@app.route("/search/")
def goods_search():
    page = request.args.get('page', 1, type=int)
    keywords = request.args.get('keywords', '', type=str)
    offset = (page - 1) * 12

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if keywords:
        cursor.execute("SELECT * FROM Goods WHERE name LIKE %s ORDER BY addtime DESC LIMIT 12 OFFSET %s",
                       ('%' + keywords + '%', offset))
    else:
        cursor.execute(
            "SELECT * FROM Goods ORDER BY addtime DESC LIMIT 12 OFFSET %s", (offset,))

    page_data = cursor.fetchall()

    cursor.execute("SELECT * FROM Goods ORDER BY views_count DESC LIMIT 7")
    hot_goods = cursor.fetchall()

    return render_template("goods_search.html", page_data=page_data, keywords=keywords, hot_goods=hot_goods)


@app.route("/cart_add/")
def cart_add():
    user_id = session.get('user_id', 0)
    goods_id = request.args.get('goods_id')
    number = request.args.get('number')

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("INSERT INTO Cart (goods_id, number, user_id) VALUES (%s, %s, %s)",
                   (goods_id, number, user_id))
    mysql.connection.commit()

    return redirect(url_for('shopping_cart'))


@app.route("/cart_clear/")
def cart_clear():
    user_id = session.get('user_id', 0)

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("DELETE FROM Cart WHERE user_id = %s", (user_id,))
    mysql.connection.commit()

    return redirect(url_for('shopping_cart'))


@app.route("/shopping_cart/")
def shopping_cart():
    user_id = session.get('user_id', 0)

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT * FROM Cart WHERE user_id = %s ORDER BY addtime DESC", (user_id,))
    cart = cursor.fetchall()

    if cart:
        return render_template('home/shopping_cart.html', cart=cart)
    else:
        return render_template('home/empty_cart.html')


@app.route("/cart_delete/<int:id>/")
def cart_delete(id=None):
    user_id = session.get('user_id', 0)

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "DELETE FROM Cart WHERE user_id = %s AND goods_id = %s", (user_id, id))
    mysql.connection.commit()

    return redirect(url_for('shopping_cart'))


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5900, debug=True)
