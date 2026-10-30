from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .models import (
    Address,
    Cart,
    CartItem,
    Category,
    Order,
    OrderItem,
    Product,
    Review,
    Subscription,
    Wishlist,
)


# =========================
# HOME
# =========================

def home(request):
    categories = Category.objects.all()[:5]
    featured_products = Product.objects.filter(
        is_available=True
    ).order_by("-created_at")[:8]

    return render(
        request,
        "petcareapp/home.html",
        {
            "categories": categories,
            "featured_products": featured_products,
        },
    )


# =========================
# PRODUCTS
# =========================

def products(request):
    query = request.GET.get("q", "").strip()
    pet_type = request.GET.get("pet_type", "").strip()

    product_list = Product.objects.filter(
        is_available=True
    ).select_related("category")

    if query:
        product_list = product_list.filter(
            Q(name__icontains=query)
            | Q(description__icontains=query)
            | Q(brand__icontains=query)
        )

    if pet_type:
        product_list = product_list.filter(pet_type=pet_type)

    categories = Category.objects.all()

    return render(
        request,
        "petcareapp/products/products.html",
        {
            "products": product_list,
            "categories": categories,
            "query": query,
            "pet_type": pet_type,
        },
    )


def product_detail(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_available=True,
    )

    reviews = product.reviews.select_related("user").order_by("-created_at")

    related_products = Product.objects.filter(
        category=product.category,
        is_available=True,
    ).exclude(
        id=product.id
    )[:4]

    return render(
        request,
        "petcareapp/products/product_detail.html",
        {
            "product": product,
            "reviews": reviews,
            "related_products": related_products,
        },
    )


# =========================
# REGISTER
# =========================

def register(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")

        if not username or not email or not password:
            messages.error(request, "Please fill in all required fields.")
            return redirect("register")

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect("register")

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        login(request, user)

        messages.success(
            request,
            "Account created successfully!"
        )

        return redirect("home")

    return render(
        request,
        "petcareapp/accounts/register.html"
    )


# =========================
# LOGIN
# =========================

def login_view(request):
    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")

        user = authenticate(
            request,
            username=username,
            password=password,
        )

        if user is not None:
            login(request, user)

            messages.success(
                request,
                f"Welcome back, {user.username}!"
            )

            return redirect("home")

        messages.error(
            request,
            "Invalid username or password."
        )

    return render(
        request,
        "petcareapp/accounts/login.html"
    )


# =========================
# LOGOUT
# =========================

def logout_view(request):
    logout(request)

    messages.success(
        request,
        "You have been logged out."
    )

    return redirect("home")


# =========================
# CART
# =========================

@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    return render(
        request,
        "petcareapp/cart/cart.html",
        {
            "cart": cart,
        },
    )


@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_available=True,
    )

    if product.stock <= 0:
        messages.error(
            request,
            "This product is currently out of stock."
        )
        return redirect("product_detail", product_id=product.id)

    cart, created = Cart.objects.get_or_create(
        user=request.user
    )

    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
    )

    if item_created:
        cart_item.quantity = 1
    else:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
        else:
            messages.warning(
                request,
                "You cannot add more than the available stock."
            )
            return redirect(
                "product_detail",
                product_id=product.id
            )

    cart_item.save()

    messages.success(
        request,
        f"{product.name} added to your cart."
    )

    return redirect("cart")


@login_required
def update_cart(request):
    if request.method != "POST":
        return redirect("cart")

    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    for item in cart.items.select_related("product"):
        quantity_key = f"quantity_{item.id}"
        quantity = request.POST.get(quantity_key)

        if quantity is None:
            continue

        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 1

        if quantity <= 0:
            item.delete()
            continue

        if quantity > item.product.stock:
            quantity = item.product.stock

        if quantity == 0:
            item.delete()
        else:
            item.quantity = quantity
            item.save()

    messages.success(
        request,
        "Cart updated successfully."
    )

    return redirect("cart")


@login_required
def remove_from_cart(request, item_id):
    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    item = get_object_or_404(
        CartItem,
        id=item_id,
        cart=cart,
    )

    item.delete()

    messages.success(
        request,
        "Item removed from cart."
    )

    return redirect("cart")


# =========================
# WISHLIST
# =========================

@login_required
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(
        user=request.user
    ).select_related("product")

    return render(
        request,
        "petcareapp/wishlist/wishlist.html",
        {
            "wishlist": wishlist_items,
        },
    )


@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_available=True,
    )

    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        product=product,
    )

    if created:
        messages.success(
            request,
            f"{product.name} added to your wishlist."
        )
    else:
        messages.info(
            request,
            "This product is already in your wishlist."
        )

    return redirect(
        "product_detail",
        product_id=product.id
    )


@login_required
def remove_from_wishlist(request, product_id):
    wishlist_item = get_object_or_404(
        Wishlist,
        user=request.user,
        product_id=product_id,
    )

    wishlist_item.delete()

    messages.success(
        request,
        "Product removed from wishlist."
    )

    return redirect("wishlist")


# =========================
# CHECKOUT
# =========================

@login_required
@transaction.atomic
def checkout(request):
    cart = get_object_or_404(
        Cart,
        user=request.user
    )

    cart_items = cart.items.select_related("product")

    if not cart_items.exists():
        messages.warning(
            request,
            "Your cart is empty."
        )
        return redirect("products")

    if request.method == "POST":
        full_name = request.POST.get("full_name", "").strip()
        phone = request.POST.get("phone", "").strip()
        address_text = request.POST.get("address", "").strip()
        city = request.POST.get("city", "").strip()
        state = request.POST.get("state", "").strip()
        pincode = request.POST.get("pincode", "").strip()

        if not all([
            full_name,
            phone,
            address_text,
            city,
            state,
            pincode,
        ]):
            messages.error(
                request,
                "Please fill in all address fields."
            )
            return redirect("checkout")

        # Check stock before creating the order
        for item in cart_items:
            if item.quantity > item.product.stock:
                messages.error(
                    request,
                    f"Not enough stock available for {item.product.name}."
                )
                return redirect("cart")

        address = Address.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address=address_text,
            city=city,
            state=state,
            pincode=pincode,
        )

        total_amount = sum(
            (
                item.product.get_price() * item.quantity
                for item in cart_items
            ),
            Decimal("0.00"),
        )

        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=total_amount,
            status="Pending",
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.get_price(),
            )

            item.product.stock -= item.quantity
            item.product.save(update_fields=["stock"])

        cart.items.all().delete()

        messages.success(
            request,
            f"Order #{order.id} placed successfully!"
        )

        return redirect("orders")

    return render(
        request,
        "petcareapp/orders/checkout.html",
        {
            "cart": cart,
            "cart_items": cart_items,
        },
    )


# =========================
# ORDERS
# =========================

@login_required
def orders(request):
    user_orders = Order.objects.filter(
        user=request.user
    ).prefetch_related("items__product").select_related(
        "address"
    )

    return render(
        request,
        "petcareapp/orders/orders.html",
        {
            "orders": user_orders,
        },
    )


# =========================
# SUBSCRIPTIONS
# =========================

@login_required
def subscriptions(request):
    user_subscriptions = Subscription.objects.filter(
        user=request.user
    ).select_related("product")

    return render(
        request,
        "petcareapp/subscriptions/subscriptions.html",
        {
            "subscriptions": user_subscriptions,
        },
    )


@login_required
def create_subscription(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_available=True,
    )

    if request.method != "POST":
        return redirect(
            "product_detail",
            product_id=product.id
        )

    frequency = request.POST.get("frequency", "Monthly")
    quantity = request.POST.get("quantity", "1")

    valid_frequencies = [
        choice[0]
        for choice in Subscription.FREQUENCY_CHOICES
    ]

    if frequency not in valid_frequencies:
        frequency = "Monthly"

    try:
        quantity = int(quantity)
    except (TypeError, ValueError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    if quantity > product.stock:
        messages.error(
            request,
            "Requested subscription quantity is greater than available stock."
        )
        return redirect(
            "product_detail",
            product_id=product.id
        )

    Subscription.objects.create(
        user=request.user,
        product=product,
        quantity=quantity,
        frequency=frequency,
        status="Active",
    )

    messages.success(
        request,
        f"Subscription created for {product.name}."
    )

    return redirect("subscriptions")


@login_required
def cancel_subscription(request, subscription_id):
    subscription = get_object_or_404(
        Subscription,
        id=subscription_id,
        user=request.user,
    )

    if request.method == "POST":
        subscription.status = "Cancelled"
        subscription.save(update_fields=["status"])

        messages.success(
            request,
            "Subscription cancelled successfully."
        )

    return redirect("subscriptions")


# =========================
# REVIEWS
# =========================

@login_required
def add_review(request, product_id):
    product = get_object_or_404(
        Product,
        id=product_id,
        is_available=True,
    )

    if request.method != "POST":
        return redirect(
            "product_detail",
            product_id=product.id
        )

    rating = request.POST.get("rating")
    comment = request.POST.get("comment", "").strip()

    try:
        rating = int(rating)
    except (TypeError, ValueError):
        rating = 0

    if rating < 1 or rating > 5:
        messages.error(
            request,
            "Rating must be between 1 and 5."
        )
        return redirect(
            "product_detail",
            product_id=product.id
        )

    if not comment:
        messages.error(
            request,
            "Please write a review."
        )
        return redirect(
            "product_detail",
            product_id=product.id
        )

    review, created = Review.objects.update_or_create(
        user=request.user,
        product=product,
        defaults={
            "rating": rating,
            "comment": comment,
        },
    )

    if created:
        messages.success(
            request,
            "Your review has been added."
        )
    else:
        messages.success(
            request,
            "Your review has been updated."
        )

    return redirect(
        "product_detail",
        product_id=product.id
    )