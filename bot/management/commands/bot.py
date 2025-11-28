# management/commands/bot.py
from django.core.management.base import BaseCommand
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from django.conf import settings

# Определяем этапы разговора
GET_NAME, GET_PHONE, GET_ADDRESS, GET_FLOWERS = range(4)

class Command(BaseCommand):
    help = 'Запускает Telegram-бота'

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обрабатывает команду /start"""
        user = update.effective_user
        await update.message.reply_html(
            f"Привет, {user.mention_html()}! Я бот для заказа цветов. Используйте /order, чтобы начать новый заказ.",
        )

    async def order(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обрабатывает команду /order"""
        # Здесь будет запуск процесса оформления заказа
        await update.message.reply_text("Давайте оформим заказ! Введите ваше имя:")

    async def start_order(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Начинает процесс заказа и запрашивает имя."""
        await update.message.reply_text("Отлично! Для начала оформления заказа введите ваше имя:")
        return GET_NAME

    async def get_name(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Сохраняет имя и запрашивает телефон."""
        context.user_data['name'] = update.message.text
        await update.message.reply_text("Введите ваш номер телефона:")
        return GET_PHONE

    async def get_phone(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Сохраняет телефон и запрашивает адрес доставки."""
        context.user_data['phone'] = update.message.text
        await update.message.reply_text("Введите адрес доставки:")
        return GET_ADDRESS

    async def get_address(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Сохраняет адрес и запрашивает пожелания к букету."""
        context.user_data['address'] = update.message.text
        await update.message.reply_text("Опишите, какой букет вы хотели бы (например, 'розы, 15 штук, красные'):")
        return GET_FLOWERS

    async def get_flowers(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Сохраняет всю информацию о заказе и завершает диалог."""
        context.user_data['flowers'] = update.message.text

        # Формируем сводку заказа
        order_summary = (
            "Спасибо! Ваш заказ принят.\n"
            f"Имя: {context.user_data['name']}\n"
            f"Телефон: {context.user_data['phone']}\n"
            f"Адрес: {context.user_data['address']}\n"
            f"Букет: {context.user_data['flowers']}"
        )
        await update.message.reply_text(order_summary)

        # TODO: Здесь будет сохранение заказа в базу данных
        # create_order(context.user_data)

        # Очищаем данные пользователя
        context.user_data.clear()
        return ConversationHandler.END

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
        """Отменяет диалог."""
        await update.message.reply_text('Заказ отменен.')
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

        application.add_handler(conv_handler)
        application.add_handler(CommandHandler("start", self.start))

        self.stdout.write(self.style.SUCCESS('Бот запущен...'))
        application.run_polling()






