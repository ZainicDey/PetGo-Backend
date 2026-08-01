import uuid
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from user.models import UserAddress
from inventory.models import Product


class Order(models.Model):
    ORDER_TYPE_CHOICES = [
        ('pos', 'POS / In-Store (Admin Created)'),
        ('online', 'Online / Direct (Customer Created)'),
        ('phone', 'Phone Order'),
    ]

    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('processing', 'Processing'),
        ('pending', 'Pending'),
        ('cancelled', 'Cancelled'),
    ]

    PAYMENT_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('online', 'Online'),
    ]

    order_number = models.CharField(max_length=30, unique=True, blank=True)
    order_type = models.CharField(
        max_length=15,
        choices=ORDER_TYPE_CHOICES,
        default='online',
        db_index=True
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders')
    address = models.ForeignKey(UserAddress, on_delete=models.SET_NULL, null=True, blank=True)

    # Financial breakdown
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    delivery_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    coupon = models.ForeignKey('marketing.Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash')

    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.order_number:
            date_str = timezone.now().strftime('%Y%m%d')
            unique_hex = uuid.uuid4().hex[:6].upper()
            self.order_number = f"ORD-{date_str}-{unique_hex}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.order_number} ({self.get_order_type_display()}) - {self.user}"



class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        product_name = self.product.name if self.product else "Deleted Product"
        return f"{self.quantity} x {product_name} (Order {self.order.order_number})"

