from rest_framework import serializers
from .models import Category, Product, Cart, CartItem, Order, OrderItem


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'slug', 'description', 'price', 'image', 'stock', 'available']


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total']
    
    def get_total(self, obj):
        return obj.get_total()


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.SerializerMethodField()
    count = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = ['id', 'items', 'total', 'count']
    
    def get_total(self, obj):
        return obj.get_total()
    
    def get_count(self, obj):
        return obj.get_count()


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    total = serializers.SerializerMethodField()
    
    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price', 'total']
    
    def get_total(self, obj):
        return obj.price * obj.quantity


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'status', 'total', 'address', 'phone', 'comment', 
            'created_at', 'items', 'payment_method', 'payment_id', 
            'payment_status'
        ]
        read_only_fields = [
            'id', 'status', 'total', 'created_at', 
            'payment_id', 'payment_status'
        ]


class OrderCreateSerializer(serializers.Serializer):
    """Сериализатор для создания заказа"""
    address = serializers.CharField()
    phone = serializers.CharField()
    comment = serializers.CharField(required=False, allow_blank=True)
    payment_method = serializers.ChoiceField(choices=['card', 'cash'], default='cash')