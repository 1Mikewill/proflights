from django.db import models
import datetime
from django.contrib.auth.models import User
from django.db.models.signals import post_save

#create customer profile
class Profile(models.Model):
    #linking everything user relation ,profile and user
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_modified = models.DateTimeField(User, auto_now=True)
    phone = models.CharField(max_length=20, blank = True)
    address1 = models.CharField(max_length=200, blank = True)
    address2 = models.CharField(max_length=200, blank = True)
    city = models.CharField(max_length=200, blank = True)
    state = models.CharField(max_length=200, blank = True)
    zipcode = models.CharField(max_length=200, blank = True)
    country = models.CharField(max_length=200, blank = True)
    old_cart = models.CharField(max_length=200, blank = True)

    def __str__(self):
        return self.user.username
    
    #create a user profile by default when signs in
def create_profile(sender, instance, created, **kwargs):
    if created:
        user_profile = Profile(user = instance)
        user_profile.save()

    #automate the creation of a profile
post_save.connect(create_profile, sender=User)

    
# Categories of products
class Category(models.Model):
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'
    
# Customers 
class Customer(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    email = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)
    
    def __str__(self):
        return f'{self.first_name} {self.last_name}'

# All of our products
class Product(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    description = models.CharField(max_length=250, default='', blank=True, null=True)
    image = models.ImageField(upload_to='uploads/product/')
    # Add sale objects
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(default=0, decimal_places=2, max_digits=6)
    
    def __str__(self):
        return self.name
    
    #Ensure the objects manager is available
    #objects = models.Manager()

# Customer orders
class Order(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    address = models.CharField(max_length=255, default='')  # Increased length for address
    date = models.DateTimeField(auto_now_add=True)  # Use DateTimeField
    status = models.BooleanField(default=False)

    def __str__(self):
        return f'Order of {self.quantity} x {self.product.name} by {self.customer.first_name} {self.customer.last_name}'