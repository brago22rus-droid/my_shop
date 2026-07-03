from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Category, Product, Cart, CartItem, Order, OrderItem
from .serializers import (
    CategorySerializer, ProductSerializer,
    CartSerializer, CartItemSerializer, OrderSerializer
)
from .email_utils import send_order_notification


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = []


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.filter(available=True)
    serializer_class = ProductSerializer
    permission_classes = []

    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        return queryset


class CartViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def get_cart(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart

    def list(self, request):
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add(self, request):
        cart = self.get_cart(request)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        product = get_object_or_404(Product, id=product_id, available=True)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def remove(self, request):
        cart = self.get_cart(request)
        item_id = request.data.get('item_id')

        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            cart_item.delete()
            return Response({'status': 'removed'})
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        cart = self.get_cart(request)
        item_id = request.data.get('item_id')
        quantity = int(request.data.get('quantity', 0))

        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            new_quantity = cart_item.quantity + quantity
            if new_quantity <= 0:
                cart_item.delete()
            else:
                cart_item.quantity = new_quantity
                cart_item.save()
            return Response({'status': 'updated'})
        except CartItem.DoesNotExist:
            return Response({'error': 'Item not found'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def clear(self, request):
        cart = self.get_cart(request)
        cart.items.all().delete()
        return Response({'status': 'cleared'})


class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def create(self, request):
        cart = get_object_or_404(Cart, user=request.user)

        if cart.items.count() == 0:
            return Response(
                {'error': 'Корзина пуста'},
                status=status.HTTP_400_BAD_REQUEST
            )

        address = request.data.get('address')
        phone = request.data.get('phone')

        if not address or not phone:
            return Response(
                {'error': 'Адрес и телефон обязательны'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for cart_item in cart.items.all():
            if cart_item.quantity > cart_item.product.stock:
                return Response(
                    {'error': f'Товара "{cart_item.product.name}" недостаточно на складе. В наличии: {cart_item.product.stock} шт.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        order = Order.objects.create(
            user=request.user,
            address=address,
            phone=phone,
            comment=request.data.get('comment', ''),
            total=cart.get_total()
        )

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.price
            )
            
            product = cart_item.product
            product.stock -= cart_item.quantity
            product.save()

        cart.items.all().delete()

        # ============================================================
        # ОТПРАВКА EMAIL УВЕДОМЛЕНИЯ
        # ============================================================
        send_order_notification(order)

        print(f"\n{'='*50}")
        print(f"📦 НОВЫЙ ЗАКАЗ #{order.id}")
        print(f"{'='*50}")
        print(f"👤 Клиент: {order.user.first_name} (@{order.user.username})")
        print(f"📍 Адрес: {order.address}")
        print(f"📞 Телефон: {order.phone}")
        print(f"💰 Сумма: {order.total} ₽")
        print(f"🕐 Время: {order.created_at.strftime('%d.%m.%Y %H:%M')}")
        print(f"\n🛒 Товары:")
        for item in order.items.all():
            print(f"  - {item.product.name} × {item.quantity} = {item.price * item.quantity} ₽")
        print(f"{'='*50}\n")

        serializer = self.get_serializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)