用户登录注册
用户列表
用户编辑
用户密码修改
查看用户详细信息


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
    return render_template('Category.html', page_data=page_data, hot_goods=hot_goods, supercat_id=supercat_id)


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

    return render_template('Game.html', goods=goods, hot_goods=hot_goods, similar_goods=similar_goods,
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
        return render_template('shopping_cart.html', cart=cart)
    else:
        return render_template('empty_cart.html')


@app.route("/cart_delete/<int:id>/")
def cart_delete(id=None):
    user_id = session.get('user_id', 0)

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "DELETE FROM Cart WHERE user_id = %s AND goods_id = %s", (user_id, id))
    mysql.connection.commit()

    return redirect(url_for('shopping_cart'))

@app.route('/category')
def category():
    return render_template('category.html')

@app.route("/game/", defaults={'id': None})
@app.route("/game/<int:id>/")
def game(id):
    if id is None:
        # Handle case where no id is provided
        return "No game id provided"
    else:
        # Handle case where id is provided
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Goods WHERE id = %s", (id,))
        goods = cursor.fetchone()
        
        if not goods:
            return "404: Goods not found", 404
            
        return render_template('game.html', goods=goods)


@app.route('/empty_cart')
def empty_cart():
    return render_template('empty_cart.html')

@app.route('/some_path')
def my_category():
    pass


        <li><a href="{{ url_for('game') }}">Game</a></li>
        <li><a href="{{ url_for('goods_search') }}">Goods_search</a></li>
        <li><a href="{{ url_for('shopping_cart') }}">Shopping_cart</a></li>
        <li><a href="{{ url_for('empty_cart') }}">Empty_cart</a></li>