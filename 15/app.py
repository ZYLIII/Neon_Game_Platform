from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
import hashlib
from decimal import Decimal

app = Flask(__name__)

app.secret_key = 'xyzsdfg'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '991105'
app.config['MYSQL_DB'] = 'web'

mysql = MySQL(app)


@app.route('/14/Static/<path:filename>')
def static_files(filename):
    return send_from_directory('Static', filename)


@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''  # Initialize message with an empty string
    if 'loggedin' in session:
        message = 'Another user is already logged in!'
        return render_template('Login.html', message=message), 403  # Return 403 Forbidden
        
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetch the user based on email only
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        user = cursor.fetchone()
        
        if user:
            # Hash the input password and compare it with the stored hashed password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            if hashed_password == user['password']:
                session['loggedin'] = True
                session['userid'] = user['userid']
                session['name'] = user['name']
                session['email'] = user['email']
                message = 'Logged in successfully!'
                return redirect(url_for('homepage'))
            else:
                message = 'Incorrect password!'
        else:
            message = 'Email not registered!'
        
    return render_template('Login.html', message=message), 401 if message else 200  # Return 401 if login fails


@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        repeat_password = request.form['repeat_password']
        contact_number = request.form['contact_number']  

        # Check if the email is already registered
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        account = cursor.fetchone()

        if account:
            message = 'User already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        elif not name or not password or not email or not contact_number:  # Added check for contact_number
            message = 'Please fill out the form!'
        elif password != repeat_password:
            message = 'Passwords do not match!'
        else:
            # Hash the password before storing it
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            cursor.execute('INSERT INTO user (name, email, password, contact_number) VALUES (%s, %s, %s, %s)',
                           (name, email, hashed_password, contact_number))  # Updated the SQL query
            mysql.connection.commit()
            message = 'New user created!'

    return render_template('register.html', message=message)

@app.route("/users", methods=['GET', 'POST'])
def users():
    if 'loggedin' in session:
        userid = session['userid']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE userid = %s', (userid,))
        user = cursor.fetchone()
        return render_template("users.html", user=user)
    return redirect(url_for('login'))


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    msg = ''
    if 'loggedin' in session:
        userid = session['userid']  # get the user id from the session
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE userid = %s', (userid, ))
        user = cursor.fetchone()
        
        if request.method == 'POST' and 'name' in request.form and 'contact_number' in request.form:
            userName = request.form['name']
            contact_number = request.form['contact_number']
            
            if not re.match(r'[A-Za-z0-9]+', userName):
                msg = 'Name must contain only characters and numbers!'
            else:
                cursor.execute('UPDATE user SET name = %s, contact_number = %s WHERE userid = %s', (userName, contact_number, userid))
                mysql.connection.commit()
                msg = 'User updated!'
                return redirect(url_for('users'))
        elif request.method == 'POST':
            msg = 'Please fill out the form!'
        return render_template("edit.html", msg=msg, user=user)
    return redirect(url_for('login'))  # Changed 'Login' to 'login' to match the correct route name.


@app.route("/password_change", methods=['GET', 'POST'])
def password_change():
    msg = ''  # Maintain a consistent variable name for the message.
    if 'loggedin' in session:
        userid = session['userid']  # Retrieve userid from the session.
        
        if request.method == 'POST' and 'password' in request.form and 'confirm_pass' in request.form:
            password = request.form['password']
            confirm_pass = request.form['confirm_pass']
            
            if not password or not confirm_pass:
                msg = 'Please fill out the form!'
            elif password != confirm_pass:
                msg = 'Passwords do not match!'
            else:
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                hashed_password = hashlib.sha256(password.encode()).hexdigest()
                
                cursor.execute('UPDATE user SET password = %s WHERE userid = %s', (hashed_password, userid))
                mysql.connection.commit()
                msg = 'Password updated successfully!'
                
        elif request.method == 'POST':
            msg = 'Please fill out the form!'
        
        return render_template("password_change.html", msg=msg, userid=userid)
    return redirect(url_for('login'))  # Maintain a consistent case in redirect URL.


@app.route('/logout')
def logout():
    # Clear the user's session
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('name', None)
    session.pop('email', None)
    
    # Redirect to the login page
    return redirect(url_for('login'))


@app.route("/delete/<int:userid>", methods=['POST'])
def delete(userid):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM user WHERE userid = %s', (userid, ))
    mysql.connection.commit()

    return redirect(url_for('Login'))


@app.route('/homepage')
def homepage():
    return render_template('homepage.html')


@app.route('/category')
def category():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Fetching Random Free Games where price is 0 or NULL
    cursor.execute('SELECT * FROM games WHERE price IS NULL OR price = 0 ORDER BY RAND() LIMIT 3')
    top_free_games = cursor.fetchall()
    
    # Fetching Random Paid Games
    cursor.execute('SELECT * FROM games WHERE price > 0 ORDER BY RAND() LIMIT 3')
    top_paid_games = cursor.fetchall()
    
    # Fetching Random Grossing Games
    cursor.execute('SELECT * FROM games ORDER BY RAND() LIMIT 3')
    top_grossing_games = cursor.fetchall()
    
    return render_template('Category.html', top_free=top_free_games, top_paid=top_paid_games, top_grossing=top_grossing_games)

@app.route('/game/<int:game_id>')
def game_detail(game_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM games WHERE game_id = %s', [game_id])
    game = cursor.fetchone()
    return render_template('game.html', game=game)


@app.route('/explore', methods=['GET', 'POST'])
def explore():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    games = None
    if request.method == 'POST':
        search = request.form['search']
        query = '%' + search + '%'
        cursor.execute('SELECT * FROM games WHERE name LIKE %s', [query])
        games = cursor.fetchall()
    return render_template('explore.html', games=games)

@app.route('/add_to_cart/<int:game_id>', methods=['POST'])
def add_to_cart(game_id):
    if 'loggedin' in session:
        user_id = session['userid']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('INSERT INTO cart (user_id, game_id) VALUES (%s, %s)', (user_id, game_id,))
        mysql.connection.commit()
        return redirect(url_for('cart'))
    return redirect(url_for('login'))


@app.route('/cart')
def cart():
    if 'loggedin' in session:
        user_id = session['userid']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM cart INNER JOIN games ON cart.game_id = games.game_id WHERE cart.user_id = %s', (user_id,))
        items = cursor.fetchall()
        total_price = sum(item['price'] for item in items)
        return render_template('cart.html', items=items, total_price=total_price)
    return redirect(url_for('login'))


@app.route('/remove_from_cart/<int:cart_id>', methods=['POST'])
def remove_from_cart(cart_id):
    if 'loggedin' in session:
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('DELETE FROM cart WHERE id = %s', (cart_id,))
        mysql.connection.commit()
        return redirect(url_for('cart'))
    return redirect(url_for('login'))


@app.route('/checkout', methods=['POST'])
def checkout():
    if 'loggedin' in session:
        user_id = session['userid']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Fetching the user's cart items
        cursor.execute('SELECT * FROM cart WHERE user_id = %s', (user_id,))
        cart_items = cursor.fetchall()

        # Adding cart items to user's library
        for item in cart_items:
            cursor.execute('INSERT INTO user_library (user_id, game_id) VALUES (%s, %s)', (user_id, item['game_id']))
        
        # Clearing the user's cart
        cursor.execute('DELETE FROM cart WHERE user_id = %s', (user_id,))
        
        mysql.connection.commit()
        return redirect(url_for('library'))
    return redirect(url_for('login'))

@app.route('/library')
def library():
    if 'loggedin' in session:
        user_id = session['userid']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user_library INNER JOIN games ON user_library.game_id = games.game_id WHERE user_library.user_id = %s', (user_id,))
        items = cursor.fetchall()
        
        cursor.execute('SELECT wallet_balance FROM user WHERE userid = %s', (user_id,))
        wallet_balance = cursor.fetchone()['wallet_balance']
        
        return render_template('library.html', items=items, wallet_balance=wallet_balance)
    return redirect(url_for('login'))


from decimal import Decimal

# ...
@app.route('/sell_game/<int:game_id>', methods=['POST'])
def sell_game(game_id):
    if 'loggedin' in session:
        user_id = session['userid']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT price FROM games WHERE game_id = %s', (game_id,))
        game_price = cursor.fetchone()['price']
        
        # Convert the float to Decimal before multiplication
        amount_to_add = game_price * Decimal('0.7')
        
        # Update user's wallet balance
        cursor.execute('UPDATE user SET wallet_balance = wallet_balance + %s WHERE userid = %s', (amount_to_add, user_id))
        
        # Remove game from user's library
        cursor.execute('DELETE FROM user_library WHERE game_id = %s AND user_id = %s', (game_id, user_id))
        
        mysql.connection.commit()
        
        return redirect(url_for('library'))
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5900, debug=True)
