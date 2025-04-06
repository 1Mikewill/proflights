from store.models import Product, Profile

class Cart():
    def __init__(self, request):
        self.session = request.session
        # Get the request
        self.request = request

        #Get the current session key if it exists
        cart = self.session.get('session_key')

        #If the session key does not exist meaning user is new, create a new one
        if 'session_key' not in request.session:
            cart = self.session['session_key'] = {}

        #Making sure the cart is available on all pages of the site
        self.cart = cart

    def db_add(self, product, quantity):
        product_id = str(product)
        product_qty = str(quantity)

        #Logic If the product is not in the cart, add it
        if product_id in self.cart:
            pass
        else:
            #self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)
         #Save the session
        self.session.modified = True

        #deals with loggedin users
        if self.request.user.is_authenticated:
            #get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # convert single quote to double e.g {'3':1}to {"3":1}
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            #update the carty to Profile model
            current_user.update(old_cart=str(carty))

    def add(self, product, quantity):
        product_id = str(product.id)
        product_qty = str(quantity)

        #Logic If the product is not in the cart, add it
        if product_id in self.cart:
            pass
        else:
            #self.cart[product_id] = {'price': str(product.price)}
            self.cart[product_id] = int(product_qty)
         #Save the session
        self.session.modified = True

        #deals with loggedin users
        if self.request.user.is_authenticated:
            #get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # convert single quote to double e.g {'3':1}to {"3":1}
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            #update the carty to Profile model
            current_user.update(old_cart=str(carty))

    def cart_total(self):
        #get prodct ids
        product_ids = self.cart.keys()
        #looking up the keys in product db model
        products = Product.objects.filter(id__in=product_ids)
        # getting quantities
        quantities = self.cart
        #count starts at 0
        total = 0

        for key, value in quantities.items():
            #convert key str into int for lookup
            key = int(key)
            for product in products:
                if product.id == key:
                    #check if product is on sale or not and output expected output
                    if product.is_sale:
                        total = total + (product.sale_price * value)
                    else:
                        total = total + (product.price * value)
        return total
                    


    def __len__(self):
        return len(self.cart)
    
    def get_prods(self):
        #get ids from cart
        product_ids = self.cart.keys()
        # use ids to lookup products in db model
        products = Product.objects.filter(id__in=product_ids)
        #return looked up products
        return products
    
    def get_quants(self):
        quantities = self.cart
        return quantities

    def update(self, product, quantity):
        product_id = str(product)
        product_qty = int(quantity)

        #get cart
        outcart = self.cart
        #update cart dictionary with py
        outcart[product_id] = product_qty
        #save the session
        self.session.modified = True
        
        thing = self.cart

        #deals with loggedin users
        if self.request.user.is_authenticated:
            #get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # convert single quote to double e.g {'3':1}to {"3":1}
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            #update the carty to Profile model
            current_user.update(old_cart=str(carty))

        return thing
    
    def delete(self, product):
        product_id = str(product)
        #delete item from cart
        if product_id in self.cart:
            del self.cart[product_id]
        
        self.session.modified = True

        #deals with loggedin users
        if self.request.user.is_authenticated:
            #get the current user profile
            current_user = Profile.objects.filter(user__id=self.request.user.id)
            # convert single quote to double e.g {'3':1}to {"3":1}
            carty = str(self.cart)
            carty = carty.replace("\'", "\"")
            #update the carty to Profile model
            current_user.update(old_cart=str(carty))