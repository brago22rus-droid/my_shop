import json
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Order
from .telegram import send_telegram_notification

logger = logging.getLogger(__name__)


@csrf_exempt
@require_POST
def yookassa_webhook(request):
    """
    Вебхук от ЮKassa для обновления статуса платежа
    """
    try:
        # Парсим данные
        data = json.loads(request.body)
        logger.info(f"📨 Получен вебхук от ЮKassa: {data}")
        
        # Проверяем событие
        event = data.get('event')
        
        if event == 'payment.succeeded':
            payment_id = data['object']['id']
            metadata = data['object'].get('metadata', {})
            order_id = metadata.get('order_id')
            
            if order_id:
                try:
                    order = Order.objects.get(id=order_id)
                    order.status = 'paid'
                    order.payment_status = 'succeeded'
                    order.save(update_fields=['status', 'payment_status'])
                    
                    # Отправляем уведомление об оплате
                    send_telegram_notification(
                        order, 
                        message=f"✅ Заказ #{order.id} успешно оплачен!"
                    )
                    
                    logger.info(f"✅ Заказ #{order_id} успешно оплачен")
                    
                    return JsonResponse({
                        'status': 'ok', 
                        'message': f'Order {order_id} paid successfully'
                    })
                    
                except Order.DoesNotExist:
                    logger.error(f"❌ Заказ {order_id} не найден")
                    return JsonResponse({
                        'status': 'error', 
                        'message': 'Order not found'
                    }, status=404)
        
        elif event == 'payment.canceled':
            payment_id = data['object']['id']
            metadata = data['object'].get('metadata', {})
            order_id = metadata.get('order_id')
            
            if order_id:
                try:
                    order = Order.objects.get(id=order_id)
                    if order.payment_status != 'succeeded':
                        order.status = 'cancelled'
                        order.payment_status = 'canceled'
                        order.save(update_fields=['status', 'payment_status'])
                        
                        send_telegram_notification(
                            order, 
                            message=f"❌ Платеж по заказу #{order.id} отменен"
                        )
                        
                        logger.info(f"❌ Платеж по заказу #{order_id} отменен")
                        
                except Order.DoesNotExist:
                    logger.error(f"❌ Заказ {order_id} не найден")
        
        # Всегда возвращаем 200 для ЮKassa, даже если ошибка
        return JsonResponse({'status': 'ok'})
        
    except json.JSONDecodeError as e:
        logger.error(f"❌ Ошибка парсинга JSON: {e}")
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON'}, status=400)
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки вебхука: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)