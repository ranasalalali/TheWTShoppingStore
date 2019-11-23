import unittest
from bottle import request, response
from http.cookies import SimpleCookie

import session
import dbschema


class MockBeakerSession(dict):
    """A Mock version of a beaker session, just a dictionary
    with a 'save' method that does nothing"""

    def save(self):
        pass

class SessionTests(unittest.TestCase):

    def setUp(self):

        # init an in-memory database
        self.db = dbschema.connect(':memory:')
        dbschema.create_tables(self.db)
        self.products = dbschema.sample_data(self.db)
        if 'beaker.session' in request.environ:
            del request.environ['beaker.session']

    def test_get_cart(self):
        """Can get the contents of the cart"""

        request.environ['beaker.session'] = MockBeakerSession({'cart': []})
        self.assertEqual([], session.get_cart_contents())

        cart = [{'id': 1, 'quantity': 3, 'name': 'test', 'cost': 123.45}]
        request.environ['beaker.session'] = {'cart': cart}
        self.assertEqual(cart, session.get_cart_contents())

    def test_add_to_cart(self):
        """We can add items to the shopping cart
        and retrieve them"""

        # We start one session
        cart = []
        request.environ['beaker.session'] = MockBeakerSession({'cart': cart})
        self.assertEqual([], session.get_cart_contents())

        # now add something to the cart
        for pname in ['Yellow Wool Jumper', 'Classic Varsity Top']:
            product =  self.products[pname]
            session.add_to_cart(self.db, product['id'], 1 )

        cart = session.get_cart_contents()
        self.assertEqual(2, len(cart))

        # check that all required fields are in every cart entry
        for entry in cart:
            self.assertIn('id', entry)
            self.assertIn('name', entry)
            self.assertIn('quantity', entry)
            self.assertIn('cost', entry)

        # We start a session again and check that the cart is empty
        cart = []
        request.environ['beaker.session'] = MockBeakerSession({'cart': cart})
        self.assertEqual([], session.get_cart_contents())

        # now add something to the cart in the new session
        for pname in ['Yellow Wool Jumper', 'Silk Summer Top', 'Zipped Jacket']:
            product =  self.products[pname]
            session.add_to_cart(self.db, product['id'], 1 )

        cart = session.get_cart_contents()
        self.assertEqual(3, len(cart))


    def test_add_nonexisting_to_cart(self):
        # We start one session
        cart = []
        request.environ['beaker.session'] = MockBeakerSession({'cart': cart})
        self.assertEqual([], session.get_cart_contents())
        product =  self.products['Classic Varsity Top']
        session.add_to_cart(self.db, product['id'], 1 )
        cart = session.get_cart_contents()
        self.assertEqual(1, len(cart))

        # check that we cannot add a non-existing object
        session.add_to_cart(self.db, 100, 2)
        cart = session.get_cart_contents()
        self.assertEqual(1, len(cart), "Error when adding non-existing object")

        # check that we cannot add an item that exceeds amount in inventory
        session.add_to_cart(self.db, 10, 100)
        cart = session.get_cart_contents()
        self.assertEqual(1, len(cart), "Quantity exceeded amount in inventory")

        # check that we cannot add an item with non-positive amount
        session.add_to_cart(self.db, 10, -3)
        cart = session.get_cart_contents()
        self.assertEqual(1, len(cart), "Adding item with negative amount")
        session.add_to_cart(self.db, 10, 0)
        cart = session.get_cart_contents()
        self.assertEqual(1, len(cart), "Adding item with zero amount")

    def test_add_wrong_amount_to_cart(self):
        # We start one session
        cart = []
        request.environ['beaker.session'] = MockBeakerSession({'cart': cart})
        self.assertEqual([], session.get_cart_contents())
        product =  self.products['Classic Varsity Top']
        session.add_to_cart(self.db, product['id'], 1 )
        cart = session.get_cart_contents()
        self.assertEqual(1, len(cart))

        # check that we cannot add an item that exceeds amount in inventory
        session.add_to_cart(self.db, 10, 100)
        cart = session.get_cart_contents()
        self.assertEqual(1, len(cart), "Quantity exceeded amount in inventory")

        # check that we cannot add an item with non-positive amount
        session.add_to_cart(self.db, 10, -3)
        cart = session.get_cart_contents()
        self.assertEqual(1, len(cart), "Adding item with negative amount")
        session.add_to_cart(self.db, 10, 0)
        cart = session.get_cart_contents()
        self.assertEqual(1, len(cart), "Adding item with zero amount")

    def test_cart_update(self):
        """We can update the quantity of an item in the cart"""

        # first need to force the creation of a session with an empty cart
        cart = []
        request.environ['beaker.session'] = MockBeakerSession({'cart': cart})

        # add something to the cart
        product =  self.products['Yellow Wool Jumper']
        quantity = 3
        session.add_to_cart(self.db, product['id'], quantity )
        cart = session.get_cart_contents()

        self.assertEqual(1, len(cart))
        # compare ids as strings to be as flexible as possible
        self.assertEqual(str(product['id']), str(cart[0]['id']))
        self.assertEqual(quantity, cart[0]['quantity'])

        # now add again to the cart, check that we still have one item and the
        # quantity is doubled
        session.add_to_cart(self.db, product['id'], quantity)
        cart = session.get_cart_contents()

        self.assertEqual(1, len(cart))
        self.assertEqual(product['id'], cart[0]['id'])
        self.assertEqual(quantity*2, cart[0]['quantity'])

        # now add a third time, this time exceeding the amount in inventory, check that
        # we still have one item and the quantity has not changed
        session.add_to_cart(self.db, product['id'], 100)
        cart = session.get_cart_contents()

        self.assertEqual(1, len(cart), "Test adding excessive quantity of products")
        self.assertEqual(product['id'], cart[0]['id'], "Test adding excessive quantity of products")
        self.assertEqual(quantity*2, cart[0]['quantity'], "Test adding excessive quantity of products")

if __name__=='__main__':
    unittest.main()
