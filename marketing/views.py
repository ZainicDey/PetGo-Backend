from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample
from .models import Coupon
from .serializers import CouponSerializer

@extend_schema_view(
    create=extend_schema(
        summary="Create a new discount coupon",
        examples=[
            OpenApiExample(
                name="Percentage Discount Coupon",
                summary="10% percentage discount capped at $20",
                value={
                    "code": "SUMMER10",
                    "discount_type": "percentage",
                    "discount_value": "10.00",
                    "min_cap": "50.00",
                    "max_cap": "20.00",
                    "open_date": "2026-08-01T00:00:00Z",
                    "close_date": "2026-08-31T23:59:59Z",
                    "is_active": True
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Flat Amount Discount Coupon",
                summary="Flat $15 dollar discount",
                value={
                    "code": "FLAT15OFF",
                    "discount_type": "flat",
                    "discount_value": "15.00",
                    "min_cap": "100.00",
                    "max_cap": None,
                    "open_date": "2026-08-01T00:00:00Z",
                    "close_date": "2026-08-31T23:59:59Z",
                    "is_active": True
                },
                request_only=True,
            ),
        ]
    )
)
class CouponViewSet(viewsets.ModelViewSet):
    queryset = Coupon.objects.all()
    serializer_class = CouponSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'uuid'


