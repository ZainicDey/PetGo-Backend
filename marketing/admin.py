from django.contrib import admin
from .models import Coupon

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_type', 'discount_value', 'min_cap', 'max_cap', 'open_date', 'close_date', 'is_active')
    list_filter = ('discount_type', 'is_active', 'open_date', 'close_date')
    search_fields = ('code',)
    readonly_fields = ('created_at', 'updated_at')

