from cart.cart import Cart
from django.contrib import messages
from django.shortcuts import redirect, render
from payment.forms import ShippingForm, PaymentForm
from payment.models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from store.models import Product, Profile
import datetime

def not_shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=False)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            
            #get the order
            order = Order.objects.filter(id=num)
            #grab date and time 
            now = datetime.datetime.now()
            #update order
            order.update(shipped=True, date_shipped=now)
            #redirect
            messages.success(request, "Shipping Status Updated")
            return redirect('home')
        
        return render(request, "payment/not_shipped_dash.html", {'orders': orders,})
    else:
        messages.success(request, "Access denied")
        return redirect('home')

def shipped_dash(request):
    if request.user.is_authenticated and request.user.is_superuser:
        orders = Order.objects.filter(shipped=True)
        if request.POST:
            status = request.POST['shipping_status']
            num = request.POST['num']
            
            #grab order
            order = Order.objects.filter(id=num)
            #grab date and time 
            now = datetime.datetime.now()
            #update order
            order.update(shipped=False)
            #redirect
            messages.success(request, "Shipping Status Updated")
            return redirect('home')

        return render(request, "payment/shipped_dash.html", {'orders': orders,})
    else:
        messages.success(request, "Access denied")
        return redirect('home')

def process_order(request):
    if request.POST:
        # Get the cart
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants
        totals = cart.cart_total()

        # Get shipping session data
        my_shipping = request.session.get('my_shipping')

        # Get order information
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        zipcode = my_shipping.get('shipping_zipcode') or my_shipping.get('shipping_zip_code', '')

        # Create shipping address
        shipping_address = (
            f"{my_shipping['shipping_address1']} "
            f"{my_shipping['shipping_address2']} "
            f"{my_shipping['shipping_city']} "
            f"{my_shipping['shipping_country']} "
            f"{zipcode}"
        )
        amount_paid = totals
        
        # Create the order
        if request.user.is_authenticated:
            user = request.user
            create_order = Order(
                user=user,
                full_name=full_name,
                email=email,
                shipping_address=shipping_address,
                amount_paid=amount_paid
            )
            create_order.save()

            # Add order items
            order_id = create_order.pk
            for product in cart_products:
                product_id = product.id
                price = product.sale_price if product.is_sale else product.price

                for key, value in quantities().items():
                    if int(key) == product.id:
                        create_order_item = OrderItem(
                            order_id=order_id,
                            product_id=product_id,
                            user=user,
                            quantity=value,
                            price=price
                        )
                        create_order_item.save()

            # Clear the cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    del request.session[key]

            messages.success(request, "Order Placed successfully")
            return redirect('home')

        else:
            create_order = Order(
                full_name=full_name,
                email=email,
                shipping_address=shipping_address,
                amount_paid=amount_paid
            )
            create_order.save()

            # Add order items
            order_id = create_order.pk
            for product in cart_products:
                product_id = product.id
                price = product.sale_price if product.is_sale else product.price

                for key, value in quantities().items():
                    if int(key) == product.id:
                        create_order_item = OrderItem(
                            order_id=order_id,
                            product_id=product_id,
                            quantity=value,
                            price=price
                        )
                        create_order_item.save()
# filtering cart 
        # Clear the cart
        for key in list(request.session.keys()):
            if key == "session_key":
                del request.session[key]

        #clear cart from Database(old_cart field)
        current_user = Profile.objects.filter(user__id=request.user.id)
        #clear shopping cart in DB(old_cart field)
        current_user.update(old_cart="")

        messages.success(request, "Order Placed successfully")
        return redirect('home')
    else:
        messages.error(request, "Access denied")
        return redirect('home')

def billing_info(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods()
        quantities = cart.get_quants
        totals = cart.cart_total()

        # Create session for shipping info
        request.session['my_shipping'] = request.POST

        # Initialize billing form
        billing_form = PaymentForm()
        
        return render(request, "payment/billing_info.html", {
            "cart_products": cart_products,
            "quantities": quantities,
            "totals": totals,
            "shipping_info": request.POST,
            "billing_form": billing_form
        })
    else:
        messages.success(request, "Access denied")
        return redirect('home')

def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods()
    quantities = cart.get_quants
    totals = cart.cart_total()
    
    if request.user.is_authenticated:
        try:
            shipping_user = ShippingAddress.objects.get(user__id=request.user.id)
            shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        except ShippingAddress.DoesNotExist:
            messages.error(request, "You need to provide a shipping address.")
            return redirect('create_shipping_address')
    else:
        shipping_form = ShippingForm(request.POST or None)

    return render(request, "payment/checkout.html", {
        "cart_products": cart_products,
        "quantities": quantities,
        "totals": totals,
        "shipping_form": shipping_form
    })

def payment_success(request):
    return render(request, "payment/payment_success.html", {})

def orders(request, pk):
    if request.user.is_authenticated and request.user.is_superuser:
        #get the order
        order = Order.objects.get(id=pk)
            #get order items
        items = OrderItem.objects.filter(order_id=pk)

        if request.POST:
            status = request.POST['shipping_status']
            #check if true or false
            if status == "true":
                #get the order
                order = Order.objects.filter(id=pk)
                #update its status
                now = datetime.datetime.now()
                order.update(shipped=True, date_shipped=now)
            else:
                #get the order
                order = Order.objects.filter(id=pk)
                #update the status
                order.update(shipped=True)
            messages.success(request, "Shipping Status Updated")
            return redirect('home')

        return render(request, "payment/orders.html", {'order':order, 'items':items})
    else:
            messages.success(request, "Access denied")
            return redirect('home')
