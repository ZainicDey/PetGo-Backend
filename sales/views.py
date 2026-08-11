from rest_framework import viewsets, permissions
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderItemSerializer

@extend_schema_view(
    create=extend_schema(
        summary="Create a new Order (POS or Online)",
        examples=[
            OpenApiExample(
                name="POS In-Store Order Example",
                summary="An order created by an Admin/Cashier in the store",
                value={
                    "order_type": "pos",
                    "user": 1,
                    "address": 1,
                    "delivery_price": "0.00",
                    "payment_method": "cash",
                    "order_status": "completed",
                    "order_items": [
                        {
                            "product": 1,
                            "quantity": 2
                        }
                    ]
                },
                request_only=True,
            ),
            OpenApiExample(
                name="Online Direct Order Example",
                summary="An order placed by a customer on the website",
                value={
                    "order_type": "online",
                    "user": 1,
                    "address": 1,
                    "delivery_price": "10.00",
                    "payment_method": "card",
                    "order_status": "pending",
                    "order_items": [
                        {
                            "product": 1,
                            "quantity": 1
                        }
                    ]
                },
                request_only=True,
            ),
        ]
    )
)
class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'uuid'


class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'uuid'

