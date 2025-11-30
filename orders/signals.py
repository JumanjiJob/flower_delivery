from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from .models import Order
from django.conf import settings
from telegram import Bot
import asyncio


@receiver(post_save, sender=Order)
def send_status_notification(sender, instance, **kwargs):
    """
    Отправляет уведомление в Telegram при изменении статуса заказа.
    """
    if instance.telegram_chat_id:
        # Сообщения для разных статусов
        status_messages = {
            'new': f"🆕 Ваш заказ №{instance.id} принят в обработку!",
            'confirmed': f"✅ Заказ №{instance.id} подтвержден! Готовим ваш букет.",
            'processing': f"🔧 Заказ №{instance.id} собирается нашими флористами.",
            'in_progress': f"🚚 Заказ №{instance.id} передан курьеру! Ожидайте доставку.",
            'delivered': f"📦 Заказ №{instance.id} доставлен! Спасибо за покупку! 🌹",
            'cancelled': f"❌ Заказ №{instance.id} отменен."
        }

        message = status_messages.get(instance.status)
        if message:
            try:
                bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
                # Используем async_to_sync для вызова асинхронного метода
                async_to_sync(bot.send_message)(
                    chat_id=instance.telegram_chat_id,
                    text=message
                )
                print(f"Уведомление отправлено для заказа {instance.id}")
            except Exception as e:
                print(f"Ошибка отправки уведомления: {e}")