import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings

# Простая имитация push-уведомлений через браузер
# В реальном проекте используй Firebase Cloud Messaging (FCM)

class PushNotification:
    def __init__(self):
        self.subscriptions = {}  # В реальном проекте храни в БД

    def send_notification(self, title, body, icon=None):
        """
        Отправляет уведомление администратору
        """
        # В реальном проекте здесь будет отправка через FCM
        # Сейчас просто логируем
        print(f"\n{'='*50}")
        print(f"🔔 PUSH УВЕДОМЛЕНИЕ")
        print(f"{'='*50}")
        print(f"📌 {title}")
        print(f"📝 {body}")
        print(f"{'='*50}\n")
        
        # Здесь можно добавить отправку через FCM
        return True

# Создаем экземпляр
push = PushNotification()


def send_order_notification(order):
    """
    Отправляет уведомление о новом заказе
    """
    title = f"📦 Новый заказ #{order.id}"
    
    items_text = []
    for item in order.items.all():
        items_text.append(f"{item.product.name} × {item.quantity}")
    
    body = f"Клиент: {order.user.first_name}\nСумма: {order.total} ₽\nТовары: {', '.join(items_text[:3])}"
    if len(items_text) > 3:
        body += f" и ещё {len(items_text) - 3} товара"
    
    push.send_notification(title, body)
    return True