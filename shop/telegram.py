import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# Замените на ваш Telegram Bot Token
TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'  # ID чата для уведомлений


def send_telegram_notification(order, message=None):
    """
    Отправка уведомления в Telegram о новом заказе
    
    Args:
        order: Объект заказа
        message: Дополнительное сообщение (опционально)
    """
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == 'YOUR_BOT_TOKEN':
        logger.warning("Telegram бот не настроен")
        return
    
    try:
        # Формируем сообщение
        if not message:
            items_text = "\n".join([
                f"  • {item.product.name} × {item.quantity} = {item.price * item.quantity} ₽"
                for item in order.items.all()
            ])
            
            message = f"""
🛍️ НОВЫЙ ЗАКАЗ #{order.id}
━━━━━━━━━━━━━━━━━━━━━
👤 Клиент: {order.user.first_name} (@{order.user.username})
📍 Адрес: {order.address}
📞 Телефон: {order.phone}
💰 Сумма: {order.total} ₽
💳 Оплата: {'Карта' if order.payment_method == 'card' else 'Наличные'}
🕐 Время: {order.created_at.strftime('%d.%m.%Y %H:%M')}

📦 Товары:
{items_text}
━━━━━━━━━━━━━━━━━━━━━
"""
        
        # Отправляем сообщение
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }
        
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            logger.info(f"✅ Уведомление о заказе #{order.id} отправлено в Telegram")
        else:
            logger.error(f"❌ Ошибка отправки в Telegram: {response.text}")
            
    except Exception as e:
        logger.error(f"❌ Ошибка отправки в Telegram: {e}")