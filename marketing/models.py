from django.db import models
from django.utils import timezone
import uuid

class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Percentage (%)'),
        ('flat', 'Flat Amount ($)'),
    ]

    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(
        max_length=15,
        choices=DISCOUNT_TYPE_CHOICES,
        default='percentage'
    )
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    
    min_cap = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Minimum order subtotal required to apply this coupon"
    )
    max_cap = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Maximum discount amount allowed (especially for percentage discounts)"
    )
    
    open_date = models.DateTimeField(help_text="When this coupon becomes active/valid")
    close_date = models.DateTimeField(help_text="When this coupon expires/closes")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.code} ({self.get_discount_type_display()}: {self.discount_value})"

    def is_valid(self, order_subtotal=0):
        now = timezone.now()
        if not self.is_active:
            return False, "Coupon is disabled."
        if now < self.open_date:
            return False, "Coupon is not active yet."
        if now > self.close_date:
            return False, "Coupon has expired."
        if order_subtotal < self.min_cap:
            return False, f"Minimum order amount of {self.min_cap} required."
        return True, "Valid"

    def calculate_discount(self, order_subtotal):
        if self.discount_type == 'flat':
            discount = self.discount_value
        else:  # percentage
            discount = (order_subtotal * self.discount_value) / 100
            
        if self.max_cap and discount > self.max_cap:
            discount = self.max_cap
        return min(discount, order_subtotal)

