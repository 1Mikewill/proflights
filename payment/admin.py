from django.contrib import admin
from .models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User

#register the models on the main admin section
admin.site.register(ShippingAddress)
admin.site.register(Order)
admin.site.register(OrderItem)

#Create an OrderItem Inline
class OrderItemInline(admin.StackedInline):
    model = OrderItem
    extra = 0

# Extend order model
class OrderAdmin(admin.ModelAdmin):
    model = Order
    fields = ['user', 'full_name', 'email', 'shipping_address', 'amount_paid', 'date_ordered', 'shipped','date_shipped']
    readonly_fields = ['date_ordered']
    inlines = [OrderItemInline]

# Unregister order model and register it again with the inline
admin.site.unregister(Order)
admin.site.register(Order, OrderAdmin)