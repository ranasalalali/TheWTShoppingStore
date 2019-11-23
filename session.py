"""
Code for handling sessions in our web application
"""

from bottle import request

import model


def add_to_cart(db, itemid, quantity):
    """This functions is what happens at the backend when the user adds a product to their cart.
    This performs some checks before the actual addition of the product.
    session - this is the session that we get using beaker, that was initialized at the start of the application
    the initialization of beaker is done at the very end of main.py inside main function
    cart - a list of dictionaries. This uses session to initialize a cart if
            is is not already contained in the beaker session.
    product - to get the details of a product based on the itemid passed.
    The checks performed in the functioned are as follows:
        1. if product exists in the database or not
        2. if the quantity selected by the user is less than or equal to what we have in the inventory
        3. if the product already exists in the cart, then update the values.

    A list of dictionaries of products is cart in the session of beaker.
    The dictionary is a key value pair of the ID, Quantity, Name and Cost of a product."""
    session = request.environ.get('beaker.session')
    cart = session.get('cart', [])
    product = model.product_get(db, itemid)
    if product:
        cost = product['unit_cost']
        name = product['name']
        inventory = product['inventory']
        if product['inventory'] >= int(quantity) >= 1:
            if cart:
                index = 0
                for product in cart:
                    if product['id'] == itemid:
                        quantity = int(product['quantity']) + int(quantity)
                        if quantity <= inventory:
                            cart[index] = {'id': itemid, 'quantity': int(quantity), 'name': name,
                                           'cost': float(quantity) * cost}
                            break
                        else:
                            break
                    index += 1
                if index >= len(cart):
                    cart.append({'id': itemid, 'quantity': int(quantity), 'name': name, 'cost': float(quantity) * cost})
            else:
                cart.append({'id': itemid, 'quantity': int(quantity), 'name': name, 'cost': float(quantity) * cost})
            session['cart'] = cart
    session.save()


def get_cart_contents():
    """Return the contents of the shopping cart as
    a list of dictionaries:
    [{'id': <id>, 'quantity': <qty>, 'name': <name>, 'cost': <cost>}, ...]
    """
    session = request.environ.get('beaker.session')
    cart = session.get('cart', [])
    return cart