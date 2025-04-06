from cart.cart import Cart
from django.contrib import messages
from django.shortcuts import redirect, render
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress

def process_order(request):
    if request.POST:
        # get the billing info from the last page
        payment_form = PaymentForm(request.POST or None)
        #get shipping session data 
        my_shipping = request.session.get('my_shipping')
        #for order confirmation in db use print(my_shipping)

        #creating a shipping address from the session  using a python dictionary
        # Handle both field name variations
        zipcode = my_shipping.get('shipping_zipcode') or my_shipping.get('shipping_zip_code', '')

        shipping_address = (
            f"{my_shipping['shipping_address1']} "
            f"{my_shipping['shipping_address2']} "
            f"{my_shipping['shipping_city']} "
            f"{my_shipping['shipping_country']} "
            f"{zipcode}"
        )
        print(shipping_address)
        messages.success(request, "Order Placed!!")
        return redirect('home')

    else:
        messages.success(request, "Access denied")
        return redirect('home')

def billing_info(request):
     if request.POST:
        #get the cart
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants
        totals = cart.cart_total()

        #create a session for the shipping info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping

        #Check to see if user is logged in 
        if request.user.is_authenticated:
            #Get the billing form
            billing_form = PaymentForm()
            return render(request, "payment/billing_info.html", {"cart_products":cart_products , "quantities":quantities , "totals":totals, "shipping_info":request.POST, "billing_form":billing_form })
        else:
             #not logged in
             return render(request, "payment/billing_info.html", {"cart_products":cart_products , "quantities":quantities , "totals":totals, "shipping_info":request.POST, "billing_form":billing_form })

        shipping_form = request.POST
        return render(request, "payment/billing_info.html", {"cart_products":cart_products , "quantities":quantities , "totals":totals, "shipping_form":shipping_form })
     else:
          messages.success(request, "Access denied")
          return redirect('home')

def checkout(request):
        #get the cart
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants
        totals = cart.cart_total()
        
        if request.user.is_authenticated:
            #checkout as a logged in user
            #shipping User
            try:
                shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
            except ShippingAddress.DoesNotExist:
                messages.error(request, "You need to provide a shipping address.")
                return redirect('create_shipping_address')  # Redirect to a page to create a new shipping address

            #shipping Form
            shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
            return render(request, "payment/checkout.html", {"cart_products":cart_products , "quantities":quantities , "totals":totals, "shipping_form":shipping_form })

        else:
            #checkout as guest
            shipping_form = ShippingForm(request.POST or None)
            return render(request, "payment/checkout.html", {"cart_products":cart_products , "quantities":quantities , "totals":totals, "shipping_form":shipping_form})

def payment_success(request):
  
    return render(request, "payment/payment_success.html", {})
