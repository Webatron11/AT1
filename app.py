# Created by Oscar Webb
# Created on roughly 11/11
# This is the python code which handles database and some website behaviour
from os import PathLike

from flask import render_template, Flask, request, redirect
from sqlite3 import connect

app = Flask(__name__)


# Used to send queries to the database
def sendDBQuery(query: str, path: str | PathLike[str]):
    database = connect(path)
    cursor = database.cursor()
    result = cursor.execute(query)
    database.commit()
    return result


# Main page - Accepts GET and POST requests in order to enable filtering the database results
@app.route('/', methods=['POST', 'GET'])
def indexPage():
    # Changes the database query depending on the button clicked
    if request.method == 'POST':
        if request.form.get('id') == 'stockUnder':
            query = '''SELECT products.id, products.sku, products.name, products.supplier, s.cost, SUM(s.change) AS "stock", datetime((SELECT MIN(stock.date) from main.stock WHERE stock.id = s.id), 'unixepoch') AS "date" 
                                FROM products 
                                INNER JOIN main.stock s on products.id = s.id 
                                WHERE (SELECT SUM(change) FROM stock WHERE id = s.id) < 5
                                GROUP BY s.id;'''
        elif request.form.get('id') == 'dateBefore':
            query = '''SELECT products.id, products.sku, products.name, products.supplier, s.cost, SUM(s.change) AS "stock", datetime((SELECT MIN(stock.date) from main.stock WHERE stock.id = s.id), 'unixepoch') AS "date" 
                                            FROM products 
                                            INNER JOIN main.stock s on products.id = s.id 
                                            WHERE "date" < 1719792000
                                            GROUP BY s.id;'''
        elif request.form.get('id') == 'normal':
            query = '''SELECT products.id, products.sku, products.name, products.supplier, s.cost, SUM(s.change) AS "stock", datetime((SELECT MIN(stock.date) from main.stock WHERE stock.id = s.id), 'unixepoch') AS "date" 
                                FROM products 
                                INNER JOIN main.stock s on products.id = s.id 
                                GROUP BY s.id;'''
    else:
        query = '''SELECT products.id, products.sku, products.name, products.supplier, s.cost, SUM(s.change) AS "stock", datetime((SELECT MIN(stock.date) from main.stock WHERE stock.id = s.id), 'unixepoch') AS "date" 
                            FROM products 
                            INNER JOIN main.stock s on products.id = s.id 
                            GROUP BY s.id;'''

    dbresult = sendDBQuery(query, './stock.db')
    rows = dbresult.fetchall()

    # Passes in array containing the database results
    return render_template('index.html', items=rows)


# Handles the update stock page - fetches all product names and ids from the database and passes them into the html
@app.route('/commands/updateStock')
def updateStockPage():
    query = '''SELECT products.id, products.name FROM products;'''
    dbresult = sendDBQuery(query, './stock.db')
    rows = dbresult.fetchall()
    items = [f"{i[1]} (ID: {i[0]})" for i in rows]

    return render_template('./commands/updateStock.html', items=items)


# Handles the add Item page - Just returns the html, nothing special
@app.route('/commands/addItem')
def addItemPage():
    return render_template("./commands/addItem.html")


# Handles the delete item page - fetches all product names and ids from the database and passes them into the html
@app.route('/commands/deleteItem')
def deleteItemPage():
    query = '''SELECT products.id, products.name FROM products;'''
    dbresult = sendDBQuery(query, './stock.db')
    rows = dbresult.fetchall()
    items = [f"{i[1]} (ID: {i[0]})" for i in rows]

    return render_template("./commands/deleteItem.html", items=items)


# Handles all form submissions. Sends various queries based off which form was submitted. Accepts POST requests only.
# Redirects to home page with code 303 to wipe HTML Post request body
@app.route('/database/', methods=['POST'])
def addItem():
    post_data = request.form.to_dict()
    query = ''''''
    if request.form.get("id") == "addItem":
        if post_data['stockCost']:
            query = f'''INSERT INTO main.products (name, supplier, sku) VALUES('{post_data['productName']}', '{post_data['productSupplier']}', '{post_data['productSKU']}');'''
            dbresult = sendDBQuery(query, './stock.db')
            query = f'''INSERT INTO main.stock VALUES({dbresult.lastrowid}, '{post_data['stockCost']}', '{post_data['stockUpdate']}', unixepoch('{post_data['stockDate']}'));'''
        else:
            query = f'''INSERT INTO main.products (name, supplier, sku) VALUES('{post_data['productName']}', '{post_data['productSupplier']}', '{post_data['productSKU']}');'''
    elif request.form.get("id") == "updateStock":
        query = f'''INSERT INTO main.stock (id, cost, change, date) VALUES('{post_data['item'].split("(")[1].removeprefix('ID: ').removesuffix(")")}', '{post_data['stockPrice']}', '{post_data['stockChange']}', unixepoch('{post_data['stockDate']}'));'''
    elif request.form.get("id") == 'deleteItem':
        query = f'''DELETE FROM main.products WHERE id = {post_data['item'].split("(")[1].removeprefix('ID: ').removesuffix(")")};'''

    sendDBQuery(query, './stock.db')

    return redirect("/", 303)


# Runs website
app.run()
