import random
from bottle import Bottle, template, static_file, request, redirect, abort

import model
import session

app = Bottle()


@app.route('/')
def index(db):
    """This is root path for the online store webapp, that gets product list containing
    all of the products from the database.
    info - a dictionary that contains two key value pairs, one has the title and the other one is the list of products."""
    info = {
        'title': "The WT Store"
    }
    list = model.product_list(db)
    info['list'] = list
    info['title'] = ""
    return template('index', info)


@app.route('/welcome')
def index(db):
    """This is a function that routes to a particular route called welcome,
    the only thing it does is that it print the title contained in the same
    dictionary variable as the previous function."""
    info = {
        'title': "Welcome to WT! The innovative online store",
        'list': {}
    }
    return template('index', info)


@app.route('/category/<cat>')
def index(db, cat):
    """This function routes the same way how we route to the root path,
    the only difference here is that it detects which category the user is looking for
    from the products. There are only two categories 'men' and 'women' so if there is a path like
    /category/child or something this function will display No prooducts in this category"""
    info = {
        'title': "The WT Store"
    }
    list = model.product_list(db, cat)
    info['list'] = list
    info['title'] = ""
    if not list:
        info = {
            'title': "No products in this category",
            'list': {}
        }
        return template('index', info)
    else:
        return template('index', info)


@app.route('/product/<id>')
def index(db, id):
    """This function is triggered when we click the title of one of the products listed in the above routes
    it gets the id from the url and displays a page that contains a detailed info of that product including
    an option to add the product to cart"""
    product = model.product_get(db, id)
    if not product:
        info = {
            'title': "The product does not exist",
            'products': {}
        }
        return template('product', info)
    else:
        products = []
        products.append(product)
        info = {
            'title': "",
            'products': products
        }
        return template('product', info)


@app.post('/cart')
def index(db):
    """This is a post method which is triggered when the user selects a quantity on the product page.
    This function further calls the add_to_cart function implemented in the session.py file
    Two values are taken from the page, product ID and quantity selected by the user.
    This function redirects to the same page but with a get method that is implemented ahead.
    To understand how add_to_cart function works, refer to the function add_to_cart in session.py"""
    session.add_to_cart(db, request.forms.get('product'), request.forms.get('quantity'))
    return redirect('cart')


@app.get('/cart')
def index(db):
    """This is the get method for the cart route that is called whenever we do not have a
    post request. Called if the user clicks the cart directly or when the function above redirects.
    This function gets the cart content uses the function in the session.py file.
    """
    cart = session.get_cart_contents()
    info = {
        'title': "",
        'products': cart
    }
    return template('cart', info)


@app.route('/static/<filename:path>')
def static(filename):
    return static_file(filename=filename, root='static')


if __name__ == '__main__':
    from bottle import run
    from bottle.ext import sqlite, beaker
    from dbschema import DATABASE_NAME

    # install the database plugin
    app.install(sqlite.Plugin(dbfile=DATABASE_NAME))

    # install beaker
    session_opts = {
        'session.type': 'memory',
    }

    beaker_app = beaker.middleware.SessionMiddleware(app, session_opts)

    run(app=beaker_app, debug=True, port=8010)
