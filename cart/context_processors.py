from .cart import Cart

 #creating context processor to make the cart available on all pages of the site
def cart(request):
    #return the default cart data
    return{'cart': Cart(request)}