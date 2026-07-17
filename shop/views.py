from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.db import transaction
import logging

from .models import Category, Product, Cart, CartItem, Order, OrderItem
from .serializers import (
    CategorySerializer, ProductSerializer,
    CartSerializer, CartItemSerializer, OrderSerializer, OrderCreateSerializer
)
from .email_utils import send_order_notification
from .telegram import send_telegram_notification
from .yookassa_client import YookassaClient

logger = logging.getLogger(__name__)


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
        """Создание заказа с поддержкой оплаты"""
        serializer = OrderCreateSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        cart = get_object_or_404(Cart, user=request.user)

        if cart.items.count() == 0:
            return Response(
                {'error': 'Корзина пуста'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем наличие товаров
        for cart_item in cart.items.all():
            if cart_item.quantity > cart_item.product.stock:
                return Response(
                    {'error': f'Товара "{cart_item.product.name}" недостаточно на складе. В наличии: {cart_item.product.stock} шт.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Создаем заказ
        with transaction.atomic():
            order = Order.objects.create(
                user=request.user,
                address=serializer.validated_data['address'],
                phone=serializer.validated_data['phone'],
                comment=serializer.validated_data.get('comment', ''),
                total=cart.get_total(),
                payment_method=serializer.validated_data.get('payment_method', 'cash')
            )

            # Переносим товары из корзины
            for cart_item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                
                # Уменьшаем остаток
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()

            # Очищаем корзину
            cart.items.all().delete()

        # Отправляем уведомления
        send_order_notification(order)
        send_telegram_notification(order)

        # 🆕 Обработка оплаты
        payment_url = None
        if order.payment_method == 'card':
            try:
                yookassa = YookassaClient()
                if yookassa.is_configured:
                    # Формируем URL для возврата
                    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:8000')
                    return_url = f"{frontend_url}/order/{order.id}/"
                    
                    # Создаем платеж
                    payment_result = yookassa.create_payment(order, return_url)
                    
                    if payment_result['success']:
                        # Сохраняем ID платежа
                        order.payment_id = payment_result['payment_id']
                        order.payment_status = 'pending'
                        order.status = 'pending'
                        order.save(update_fields=['payment_id', 'payment_status', 'status'])
                        
                        payment_url = payment_result['confirmation_url']
                        logger.info(f"Платеж создан для заказа {order.id}: {payment_result['payment_id']}")
                    else:
                        # Если не удалось создать платеж, но заказ уже создан
                        logger.error(f"Ошибка создания платежа: {payment_result.get('error')}")
                        # Статус заказа не меняем, но добавляем в ответ информацию об ошибке
                else:
                    logger.warning("ЮKassa не сконфигурирована, оплата картой недоступна")
            except Exception as e:
                logger.error(f"Ошибка при создании платежа: {e}")

        # Формируем ответ
        response_data = OrderSerializer(order).data
        if payment_url:
            response_data['payment_url'] = payment_url
        
        return Response(response_data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'])
    def payment_status(self, request, pk=None):
        """Проверка статуса оплаты"""
        order = self.get_object()
        
        if not order.payment_id:
            return Response({
                'payment_method': order.payment_method,
                'payment_status': 'no_payment',
                'message': 'Оплата не требуется или не была инициирована'
            })
        
        try:
            yookassa = YookassaClient()
            status_info = yookassa.get_payment_status(order.payment_id)
            
            if status_info['success']:
                # Обновляем статус заказа если платеж успешен
                if status_info['status'] == 'succeeded' and status_info['paid']:
                    if order.status != 'paid':
                        order.status = 'paid'
                        order.payment_status = 'succeeded'
                        order.save(update_fields=['status', 'payment_status'])
                
                return Response({
                    'payment_method': order.payment_method,
                    'payment_status': order.payment_status,
                    'status': status_info['status'],
                    'paid': status_info['paid'],
                    'amount': status_info.get('amount')
                })
            else:
                return Response({
                    'error': status_info.get('error', 'Ошибка проверки платежа')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            logger.error(f"Ошибка проверки статуса платежа: {e}")
            return Response({
                'error': 'Ошибка проверки платежа'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)