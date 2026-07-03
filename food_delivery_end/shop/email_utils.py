from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_order_notification(order):
    """
    Отправляет email-уведомление о новом заказе
    """
    # Формируем список товаров
    items_html = ""
    items_text = ""
    for item in order.items.all():
        total = item.price * item.quantity
        items_html += f"""
            <tr>
                <td style="padding:8px;border-bottom:1px solid #eee;">{item.product.name}</td>
                <td style="padding:8px;border-bottom:1px solid #eee;text-align:center;">×{item.quantity}</td>
                <td style="padding:8px;border-bottom:1px solid #eee;text-align:right;">{total} ₽</td>
            </tr>
        """
        items_text += f"  • {item.product.name} × {item.quantity} = {total} ₽\n"

    # HTML-письмо (красивое)
    html_message = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: Arial, sans-serif; color: #1a1a2e; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #ff6b35, #f7931e); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
            .content {{ background: #f8f9fa; padding: 20px; border-radius: 0 0 10px 10px; }}
            .order-info {{ background: white; padding: 15px; border-radius: 8px; margin: 10px 0; }}
            .order-info b {{ color: #ff6b35; }}
            table {{ width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; }}
            th {{ background: #ff6b35; color: white; padding: 10px; text-align: left; }}
            td {{ padding: 8px; border-bottom: 1px solid #eee; }}
            .total {{ font-size: 18px; font-weight: bold; color: #ff6b35; text-align: right; padding: 10px; }}
            .footer {{ text-align: center; color: #868e96; font-size: 12px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1 style="margin:0;">🍕 Новый заказ</h1>
                <p style="margin:5px 0 0 0;opacity:0.9;">Заказ #{order.id}</p>
            </div>
            <div class="content">
                <div class="order-info">
                    <p><b>👤 Клиент:</b> {order.user.first_name} (@{order.user.username})</p>
                    <p><b>📍 Адрес:</b> {order.address}</p>
                    <p><b>📞 Телефон:</b> {order.phone}</p>
                    <p><b>🕐 Время:</b> {order.created_at.strftime('%d.%m.%Y %H:%M')}</p>
                </div>

                <h3 style="margin:15px 0 10px 0;">🛒 Товары:</h3>
                <table>
                    <tr>
                        <th>Товар</th>
                        <th style="text-align:center;">Кол-во</th>
                        <th style="text-align:right;">Цена</th>
                    </tr>
                    {items_html}
                    <tr>
                        <td colspan="2" style="text-align:right;font-weight:bold;padding:10px;">ИТОГО:</td>
                        <td style="text-align:right;font-weight:bold;color:#ff6b35;padding:10px;">{order.total} ₽</td>
                    </tr>
                </table>

                <div class="footer">
                    <p>Это письмо отправлено автоматически с сайта доставки продуктов.</p>
                    <p>Для управления заказами перейдите в <a href="http://127.0.0.1:8000/admin/">админку</a>.</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    # Текстовая версия (для почтовых клиентов без HTML)
    plain_message = f"""
    ═══════════════════════════════════════
    🍕 НОВЫЙ ЗАКАЗ #{order.id}
    ═══════════════════════════════════════

    👤 Клиент: {order.user.first_name} (@{order.user.username})
    📍 Адрес: {order.address}
    📞 Телефон: {order.phone}
    💰 Сумма: {order.total} ₽
    🕐 Время: {order.created_at.strftime('%d.%m.%Y %H:%M')}

    🛒 Товары:
    {items_text}
    ═══════════════════════════════════════

    Для управления заказами перейдите в админку.
    """

    try:
        send_mail(
            subject=f'📦 Новый заказ #{order.id}',
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        print(f"✅ Email о заказе #{order.id} отправлен на {settings.ADMIN_EMAIL}")
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки email: {e}")
        return False