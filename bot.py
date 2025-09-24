#бот для агрегации пересланных ему сообщений
import asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters


user_notes = {}
user_tasks = {}

async def send_merged_text(user_id, context: ContextTypes.DEFAULT_TYPE):
    """Отправляем объединённый текст пользователю"""
    notes = user_notes.get(user_id, [])
    if notes:
        merged_text = "\n---\n".join(notes)
        await context.bot.send_message(chat_id=user_id, text=merged_text)
        user_notes[user_id] = []  # очищаем после отправки
        user_tasks.pop(user_id, None)  # удаляем задачу таймера

async def handle_forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    text = msg.text or msg.caption
    if not text:
        return

    user_id = msg.chat.id

    # Добавляем текст в список
    user_notes.setdefault(user_id, []).append(text)

    # Если есть уже задача таймера — отменяем её
    if user_id in user_tasks:
        user_tasks[user_id].cancel()

    # Создаём новую задачу, которая отправит текст через 1.5 секунды
    user_tasks[user_id] = context.application.create_task(timer_send(user_id, context))

async def timer_send(user_id, context):
    try:
        await asyncio.sleep(1.5)  # ждём паузу после последнего сообщения
        await send_merged_text(user_id, context)
    except asyncio.CancelledError:
        pass  # если пришло новое сообщение, таймер отменён

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Бот активен и готов принимать пересланные сообщения!")

def main():
    TOKEN = os.environ.get("TELEGRAM_TOKEN")
    PORT = int(os.environ.get("PORT", 8443))  # Render предоставляет порт через переменную окружения
    APP_NAME = os.environ.get("RENDER_SERVICE_NAME")  # Имя сервиса на Render


    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.FORWARDED & (filters.TEXT | filters.CAPTION), handle_forward))

    #app.run_polling()
    WEBHOOK_PATH = "/webhook"
    url = f"https://{APP_NAME}.onrender.com{WEBHOOK_PATH}"
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        webhook_url=url
        #webhook_path=WEBHOOK_PATH
        )

if __name__ == "__main__":
    main()