from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from django.conf import settings
from django.utils import timezone
from asgiref.sync import sync_to_async
from datetime import timedelta
import re

# Импорты ваших моделей
from orders.models import Order, OrderItem
from catalog.models import Product
from django.contrib.auth.models import User

# Определяем этапы разговора
GET_NAME, GET_PHONE, GET_ADDRESS, GET_FLOWERS = range(4)


# Синхронная функция для создания заказа
def create_order_sync(user_data, telegram_user=None):
    """
    Создает запись заказа в базе данных на основе user_data.
    """
    try:
        # 1. Подготавливаем данные для заказа
        delivery_time = timezone.now() + timedelta(hours=2)

        # 2. Создаем заказ
        new_order = Order.objects.create(
            customer_name=user_data['name'],
            customer_phone=user_data['phone'],
            delivery_address=user_data['address'],
            delivery_time=delivery_time,
            status='new',
            payment_method='cash',
            comment=f"Заказ из Telegram бота:\n{user_data['flowers']}",
            user=telegram_user,
            customer_email=user_data.get('email', ''),
            total_price=0
        )

        # 3. Создаем OrderItem с базовым продуктом
        # Ищем базовый продукт для индивидуальных букетов
        try:
            base_product = Product.objects.get(name="Индивидуальный букет")
        except Product.DoesNotExist:
            # Создаем базовый продукт, если не существует
            from catalog.models import Category
            try:
                category = Category.objects.first()
                if not category:
                    category = Category.objects.create(
                        name="Индивидуальные заказы",
                        description="Категория для индивидуальных заказов из Telegram"
                    )

                base_product = Product.objects.create(
                    name="Индивидуальный букет",
                    description='Индивидуальный букет по пожеланиям клиента',
                    price=1000,
                    category=category,
                    is_available=True
                )
            except Exception as e:
                print(f"Ошибка при создании базового продукта: {e}")
                return None

        # Создаем элемент заказа
        order_item = OrderItem.objects.create(
            order=new_order,
            product=base_product,
            quantity=1,
            price=base_product.price
        )

        # 4. Обновляем общую стоимость заказа
        new_order.update_total_price()

        return new_order

    except Exception as e:
        print(f"Ошибка при создании заказа: {e}")
        return None


# Асинхронная обертка для синхронной функции
create_order_async = sync_to_async(create_order_sync)


class Command(BaseCommand):
    help = 'Запускает Telegram-бота'

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обрабатывает команду /start"""
        user = update.effective_user
        await update.message.reply_html(
            f"Привет, {user.mention_html()}! 🌹 Я бот для заказа цветов.\n\n"
            f"Используйте /order, чтобы начать новый заказ.\n"
            f"Используйте /help, чтобы увидеть список команд.",
        )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обрабатывает команду /help"""
        help_text = """
📋 Доступные команды:

/start - Начать работу с ботом
/order - Оформить новый заказ цветов
/help - Показать эту справку

Процесс заказа:
1. Введите ваше имя
2. Укажите номер телефона
3. Введите адрес доставки
4. Опишите желаемый букет

Мы свяжемся с вами для уточнения деталей!
        """
        await update.message.reply_text(help_text)

    async def start_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Начинает процесс заказа и запрашивает имя."""
        await update.message.reply_text(
            "🌹 Отлично! Давайте оформим заказ цветов!\n\n"
            "Для начала введите ваше имя:"
        )
        return GET_NAME

    async def get_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Сохраняет имя и запрашивает телефон."""
        name = update.message.text.strip()
        if len(name) < 2:
            await update.message.reply_text("Пожалуйста, введите корректное имя (минимум 2 символа):")
            return GET_NAME

        context.user_data['name'] = name
        await update.message.reply_text(
            "📞 Теперь введите ваш номер телефона для связи:\n"
            "Например: +7 999 123-45-67"
        )
        return GET_PHONE

    async def get_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Сохраняет телефон и запрашивает адрес доставки."""
        phone = update.message.text.strip()

        # Простая валидация телефона
        phone_pattern = r'^[\+]?[0-9\s\-\(\)]+$'
        if not re.match(phone_pattern, phone) or len(phone) < 5:
            await update.message.reply_text("Пожалуйста, введите корректный номер телефона:")
            return GET_PHONE

        context.user_data['phone'] = phone
        await update.message.reply_text(
            "🏠 Введите адрес доставки:\n"
            "Улица, дом, квартира (если нужно)"
        )
        return GET_ADDRESS

    async def get_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Сохраняет адрес и запрашивает пожелания к букету."""
        address = update.message.text.strip()
        if len(address) < 5:
            await update.message.reply_text("Пожалуйста, введите более подробный адрес:")
            return GET_ADDRESS

        context.user_data['address'] = address
        await update.message.reply_text(
            "💐 Опишите, какой букет вы хотели бы заказать:\n\n"
            "Например:\n"
            "• 'Красные розы, 15 штук'\n"
            "• 'Свадебный букет из белых лилий'\n"
            "• 'Букет тюльпанов в корзине'\n"
            "• Или просто ваши пожелания и бюджет"
        )
        return GET_FLOWERS

    async def get_flowers(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Сохраняет всю информацию о заказе и завершает диалог."""
        flowers_description = update.message.text.strip()
        context.user_data['flowers'] = flowers_description

        # Формируем сводку заказа
        order_summary = (
            "✅ Спасибо! Ваш заказ принят!\n\n"
            f"📋 Детали заказа:\n"
            f"• Имя: {context.user_data['name']}\n"
            f"• Телефон: {context.user_data['phone']}\n"
            f"• Адрес: {context.user_data['address']}\n"
            f"• Букет: {context.user_data['flowers']}\n\n"
            "📞 Мы свяжемся с вами в ближайшее время для подтверждения заказа!\n"
            "⏱️ Примерное время доставки: через 2 часа"
        )

        await update.message.reply_text(order_summary)

        # Сохраняем заказ в базу данных с использованием sync_to_async
        telegram_user = None

        try:
            order = await create_order_async(context.user_data, telegram_user)

            if order:
                await update.message.reply_text(
                    f"📦 Ваш заказ №{order.id} передан флористам!\n"
                    f"Следите за статусом заказа в этом чате."
                )
            else:
                await update.message.reply_text(
                    "⚠️ Произошла ошибка при создании заказа. "
                    "Пожалуйста, свяжитесь с нами по телефону напрямую."
                )
        except Exception as e:
            await update.message.reply_text(
                "⚠️ Произошла ошибка при сохранении заказа. "
                "Но мы получили вашу заявку и свяжемся с вами!"
            )
            self.stdout.write(self.style.ERROR(f'Ошибка при создании заказа: {e}'))

        # Очищаем данные пользователя
        context.user_data.clear()
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Отменяет диалог."""
        await update.message.reply_text(
            '❌ Заказ отменен.\n'
            'Если передумаете - используйте /order для нового заказа!'
        )
        context.user_data.clear()
        return ConversationHandler.END

    def handle(self, *args, **options):
        application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

        # Настраиваем обработчик диалога (ConversationHandler)
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('order', self.start_order)],
            states={
                GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_name)],
                GET_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_phone)],
                GET_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_address)],
                GET_FLOWERS: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.get_flowers)],
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )

        # Добавляем обработчики команд
        application.add_handler(conv_handler)
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))

        self.stdout.write(self.style.SUCCESS('🤖 Бот запущен...'))
        application.run_polling()