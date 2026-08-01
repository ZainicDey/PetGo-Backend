from rest_framework import serializers
from .models import Coupon

class CouponSerializer(serializers.ModelSerializer):
    discount_type = serializers.ChoiceField(
        choices=Coupon.DISCOUNT_TYPE_CHOICES,
        help_text="Type of discount. Allowed values: 'percentage' or 'flat'."
    )

    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


