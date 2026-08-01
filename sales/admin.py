from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('unit_price', 'total_price')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'order_type', 'user', 'total_price', 'payment_method', 'order_status', 'created_at')
    list_filter = ('order_type', 'order_status', 'payment_method', 'created_at')
    search_fields = ('order_number', 'user__username', 'user__email')
    inlines = [OrderItemInline]
    readonly_fields = ('subtotal', 'total_price', 'coupon_discount', 'created_at', 'updated_at')


