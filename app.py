from flask import render_template, Flask
from sqlite3 import connect

app = Flask(__name__)


@app.route('/')
def index():
    database = connect("./database.db")

    # Select all rows - product id, product name, product supplier, cost and stock.
    # stock should be sum(stock.stock), grouped by id.
    # cost should be the most recent cost from stock.cost

    query = '''SELECT products.id, products.name, products.supplier, s.cost, SUM(s.change) AS "stock" 
                FROM products 
                INNER JOIN main.stock s on products.id = s.id 
                GROUP BY s.id;'''
    rows = database.execute(query).fetchall()
    database.close()

    return render_template('index.html', items=rows)


@app.route('/commands/addItem')
def addItem():


    database = connect("./database.db")



app.run()
