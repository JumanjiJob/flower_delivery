
from django.core.management.base import BaseCommand
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from django.conf import settings

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

    def handle(self, *args, **options):
        # Создаем и настраиваем приложение
        application = ApplicationBuilder().token(settings.TELEGRAM_BOT_TOKEN).build()

        # Добавляем обработчики команд
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("order", self.order))

        # Запускаем бота в режиме поллинга
        self.stdout.write(self.style.SUCCESS('Бот запущен...'))
        application.run_polling()