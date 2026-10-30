from django.urls import path
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Products
    path('products/', views.products, name='products'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),

    # Accounts
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Wishlist
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),

    # Orders
    path('checkout/', views.checkout, name='checkout'),
    path('orders/', views.orders, name='orders'),

    # Subscriptions
    path('subscriptions/', views.subscriptions, name='subscriptions'),
    path(
        'subscriptions/create/<int:product_id>/',
        views.create_subscription,
        name='create_subscription'
    ),
    path(
        'subscriptions/cancel/<int:subscription_id>/',
        views.cancel_subscription,
        name='cancel_subscription'
    ),

    # Reviews
    path(
        'reviews/<int:product_id>/',
        views.add_review,
        name='add_review'
    ),
]