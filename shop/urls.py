from django.urls import path, include
from django.views.decorators.csrf import csrf_exempt
from rest_framework.routers import DefaultRouter
from . import views
from .auth_views import SimpleAuthView
from .webhook_views import yookassa_webhook

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'cart', views.CartViewSet, basename='cart')
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', csrf_exempt(SimpleAuthView.as_view()), name='auth'),
    # 🆕 Вебхук для ЮKassa
    path('webhook/yookassa/', yookassa_webhook, name='yookassa_webhook'),
]