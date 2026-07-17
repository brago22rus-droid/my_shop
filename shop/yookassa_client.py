import uuid
import logging
from yookassa import Configuration, Payment
from django.conf import settings

logger = logging.getLogger(__name__)


class YookassaClient:
    def __init__(self):
        """Инициализация клиента ЮKassa"""
        self.is_configured = False
        try:
            shop_id = getattr(settings, 'YOOKASSA_SHOP_ID', None)
            secret_key = getattr(settings, 'YOOKASSA_SECRET_KEY', None)
            
            if shop_id and secret_key:
                Configuration.account_id = shop_id
                Configuration.secret_key = secret_key
                self.is_configured = True
                logger.info("✅ ЮKassa успешно сконфигурирована")
            else:
                logger.warning("⚠️ ЮKassa не сконфигурирована: отсутствуют ключи")
        except Exception as e:
            logger.error(f"❌ Ошибка конфигурации ЮKassa: {e}")

    def create_payment(self, order, return_url):
        """
        Создание платежа в ЮKassa
        
        Args:
            order: Объект заказа
            return_url: URL для возврата после оплаты
            
        Returns:
            dict: Данные платежа
        """
        if not self.is_configured:
            return {
                'success': False,
                'error': 'ЮKassa не сконфигурирована'
            }
        
        try:
            # Формируем описание заказа
            description = f"Заказ #{order.id} в доставке"
            
            # Создаем платеж
            payment = Payment.create({
                "amount": {
                    "value": str(float(order.total)),
                    "currency": "RUB"
                },
                "confirmation": {
                    "type": "redirect",
                    "return_url": return_url
                },
                "capture": True,
                "description": description,
                "metadata": {
                    "order_id": str(order.id),
                    "user_id": str(order.user.id)
                }
            }, uuid.uuid4())
            
            logger.info(f"✅ Платеж создан: {payment.id} для заказа {order.id}")
            
            return {
                'success': True,
                'payment_id': payment.id,
                'status': payment.status,
                'confirmation_url': payment.confirmation.confirmation_url
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка создания платежа: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_payment_status(self, payment_id):
        """
        Проверка статуса платежа
        
        Args:
            payment_id: ID платежа в ЮKassa
            
        Returns:
            dict: Статус платежа
        """
        if not self.is_configured:
            return {
                'success': False,
                'error': 'ЮKassa не сконфигурирована'
            }
        
        try:
            payment = Payment.find_one(payment_id)
            
            return {
                'success': True,
                'status': payment.status,
                'paid': payment.paid,
                'amount': payment.amount.value
            }
            
        except Exception as e:
            logger.error(f"❌ Ошибка получения статуса платежа: {e}")
            return {
                'success': False,
                'error': str(e)
            }