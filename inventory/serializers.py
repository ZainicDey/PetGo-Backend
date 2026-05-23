from rest_framework import serializers
from . import models

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Category
        fields = '__all__'
        read_only_fields = ['id']

class BrandSerializer(serializers.ModelSerializer):
    class Meta: 
        model = models.Brand
        fields = '__all__'
        read_only_fields = ['id']
class ProductSerializer(serializers.ModelSerializer):
    category = serializers.SlugRelatedField(
        slug_field='name',
        queryset=models.Category.objects.all()
    )
    brand = serializers.SlugRelatedField(
        slug_field='name',
        queryset=models.Brand.objects.all()
    )
    class Meta:
        model = models.Product
        fields = '__all__'
        read_only_fields = ['id']

    def to_internal_value(self, data):
        # Convert 'category' to lowercase before field-level processing
        data = data.copy()  # avoid mutating original input
        if 'category' in data and isinstance(data['category'], str):
            data['category'] = data['category'].lower()
        if 'brand' in data and isinstance(data['brand'], str):
            data['brand'] = data['brand'].lower()
        return super().to_internal_value(data)
