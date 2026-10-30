from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    PET_CHOICES = [
        ("Dog", "Dog"),
        ("Cat", "Cat"),
        ("Bird", "Bird"),
        ("Fish", "Fish"),
        ("Small Pet", "Small Pet"),
    ]

    name = models.CharField(max_length=100)
    pet_type = models.CharField(max_length=50, choices=PET_CHOICES)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.pet_type} - {self.name}"


class Product(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    discount_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products"
    )

    pet_type = models.CharField(
        max_length=50,
        choices=Category.PET_CHOICES
    )

    brand = models.CharField(
        max_length=100,
        blank=True
    )

    stock = models.PositiveIntegerField(default=0)

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True
    )

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.name

    def get_price(self):
        if self.discount_price is not None:
            return self.discount_price
        return self.price


class Address(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses"
    )

    full_name = models.CharField(
        max_length=150
    )

    phone = models.CharField(
        max_length=15
    )

    address = models.TextField()

    city = models.CharField(
        max_length=100
    )

    state = models.CharField(
        max_length=100
    )

    pincode = models.CharField(
        max_length=10
    )

    def __str__(self):
        return f"{self.full_name} - {self.city}"


class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="cart"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Cart - {self.user.username}"

    def total_price(self):
        return sum(
            item.total_price()
            for item in self.items.all()
        )


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    def total_price(self):
        return self.product.get_price() * self.quantity

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="wishlist"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    added_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("Confirmed", "Confirmed"),
        ("Shipped", "Shipped"),
        ("Delivered", "Delivered"),
        ("Cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Pending"
    )

    ordered_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        null=True
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    def total_price(self):
        return self.price * self.quantity

    def __str__(self):
        return f"Order #{self.order.id} - {self.product}"


class Subscription(models.Model):
    FREQUENCY_CHOICES = [
        ("Weekly", "Weekly"),
        ("Biweekly", "Biweekly"),
        ("Monthly", "Monthly"),
        ("Quarterly", "Quarterly"),
    ]

    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Paused", "Paused"),
        ("Cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="subscriptions"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(
        default=1
    )

    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Active"
    )

    next_delivery = models.DateField(
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class Review(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews"
    )

    rating = models.PositiveIntegerField()

    comment = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.product.name} - {self.rating}/5"