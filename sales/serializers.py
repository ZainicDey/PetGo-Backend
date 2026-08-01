from rest_framework import serializers
from .models import Order, OrderItem
from inventory.models import Product
from inventory.serializers import ProductSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product_details = ProductSerializer(source='product', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'order', 'product', 'product_details', 'quantity', 'unit_price', 'total_price']
        read_only_fields = ['id', 'order', 'unit_price', 'total_price']


class OrderItemCreateSerializer(serializers.Serializer):
    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all())
    quantity = serializers.IntegerField(min_value=1)
    unit_price = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    order_items = OrderItemCreateSerializer(many=True, write_only=True, required=False)
    order_type_display = serializers.CharField(source='get_order_type_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'order_type', 'order_type_display',
            'user', 'address', 'subtotal', 'delivery_price',
            'coupon', 'coupon_discount', 'total_price',
            'payment_method', 'order_status',
            'items', 'order_items', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'subtotal', 'coupon_discount', 'total_price',
            'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        order_items_data = validated_data.pop('order_items', [])
        order = Order.objects.create(**validated_data)

        subtotal = 0
        for item_data in order_items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            unit_price = item_data.get('unit_price', product.offer_price or product.regular_price)
            total_price = unit_price * quantity
            subtotal += total_price

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price
            )

        order.subtotal = subtotal
        if order.coupon and order.coupon.is_active:
            order.coupon_discount = order.coupon.calculate_discount(subtotal)
        else:
            order.coupon_discount = 0

        order.total_price = subtotal + order.delivery_price - order.coupon_discount
        order.save()
        return order

