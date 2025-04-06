import json  # javascript object notation

from cart.cart import Cart
from django import forms
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q  # for multiple queries
from django.shortcuts import redirect, render
from .forms import ChangePasswordForm, SignUpForm, UpdateUserForm, UserInfoForm

from payment.forms import ShippingForm
from payment.models import ShippingAddress

from .models import Category, Product, Profile


def search(request):
    #determine if user filled out the form
    if request.method == "POST":
        searched = request.POST['searched']
        #Query the Products DB model (icontains= insensitive case so no case sensitiivity for the search)
        searched = Product.objects.filter(Q(name__icontains=searched) | Q(description__icontains=searched))
        # test for null
        if not searched:
            messages.success(request, "Thet Product does not exist!!  Please Try Again...")
            return render(request, "search.html", {})
        else:
            return render(request, "search.html", {'searched':searched})
    else:
        return render(request, "search.html", {})

def update_info(request):
    if request.user.is_authenticated:
        #get current user
        current_user = Profile.objects.get(user__id=request.user.id)
        #Get current User's Shipping info
        shipping_user = ShippingAddress.objects.get(user__id=request.user.id)

        #get original user form
        form = UserInfoForm(request.POST or None, instance=current_user)
        #get user's Shipping form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        if form.is_valid() and shipping_form.is_valid:
            #save original form
            form.save()
            #save shipping form
            shipping_form.save()

            messages.success(request, "User Information updated successfully")
            return redirect('home')
        return render(request, 'update_info.html', {'form': form, 'shipping_form': shipping_form })
    else:
        messages.success(request, "You have to be logged in to view this page...")
        return redirect('home')
    

def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        #did they fill out the form
        if request.method == 'POST':
            form = ChangePasswordForm(current_user, request.POST)
            #is the form valid
            if form.is_valid():
                form.save()
                login(request, current_user)
                messages.success(request, "Your Password was updated successfully...")
                login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')
        else:
            form = ChangePasswordForm(current_user)
            return render(request, "update_password.html", {'form': form})
    else:
        messages.success(request, "You must be logged in to view your pages")


def update_user(request):
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        user_form = UpdateUserForm(request.POST or None, instance=current_user)

        if user_form.is_valid():
            user_form.save()
            login(request, current_user)
            messages.success(request, "User details updated successfully")
            return redirect('home')
        return render(request, 'update_user.html', {'user_form': user_form})
    
    else:
        messages.success(request, "User details already exist")
        return redirect('home')


def category_summary(request):
    categories = Category.objects.all()
    return render(request, 'category_summary.html',{"categories":categories})

def category(request, foo):
    # Replace hyphens with spaces
    foo = foo.replace('-', ' ')
    # Grab category from the url
    try:
        # Look up the category
        category = Category.objects.get(name=foo)
        products = Product.objects.filter(category=category)
        return render(request, 'category.html', {'products': products, 'category': category})
    except:  # Specific exception handling
        messages.success(request, "Category does not exist")  # Changed to error message
    return redirect('home')

def product(request, pk):
    try:
        product = Product.objects.get(id=pk)
        return render(request, 'product.html', {'product': product})
    except Product.DoesNotExist:  # Added exception handling
        messages.error(request, "Product does not exist")  # Error message for product not found
        return redirect('home')

def home(request):
    products = Product.objects.all()
    return render(request, 'home.html',{'products': products})

def about(request):
    return render(request, 'about.html', {})

def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)

            #do some cart stuff
            current_user = Profile.objects.get(user__id=request.user.id)
            #get saved cart from DB
            saved_cart = current_user.old_cart
            #convert DB string to python dictionary
            if saved_cart:
                #convert to dictionary using json
                converted_cart = json.loads(saved_cart)
                #add losded cart dict to ths session
                cart = Cart(request)
                #loop through the cart and the items from DB (python dict are in pairs{"key":value} form)
                for key,value in converted_cart.items():
                    cart.db_add(product=key, quantity=value)

            messages.success(request, "You have been logged in successfully")  # Corrected message
            return redirect('home')
        else:
            messages.error(request, "There was an error, please try again")  # Changed to error message
            return redirect('login')
    else:
        return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out....Thanks for stopping by...")
    return redirect('home')

def register_user(request):
    form = SignUpForm()
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            # Login user after registration
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "User Creation Successful... Fill Out The User Info Below....")
            return redirect('update_info')
        else:
            messages.error(request, "There was an error during registration. Please try again")  # Changed to error message
            return redirect('register')
    else:
        return render(request, 'register.html', {'form': form})
