from django.contrib import admin

from .models import (
    Category,
    Product,
    Address,
    Cart,
    CartItem,
    Wishlist,
    Order,
    OrderItem,
    Subscription,
    Review,
)


admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Address)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Wishlist)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Subscription)
admin.site.register(Review)