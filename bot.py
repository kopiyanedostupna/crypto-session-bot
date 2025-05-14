import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.ext import JobQueue
from datetime import time

import os

# Получаем токен из переменной окружения
BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Словарь сессий: название -> время и сообщение
SESSIONS = {
    "Азиатская сессия": (time(hour=2, minute=0), "🕑 Азиатская сессия открылась."),
    "Европейская сессия": (time(hour=10, minute=0), "🕙 Европейская сессия открылась."),
    "Американская сессия": (time(hour=16, minute=30), "🕟 Американская сессия открылась."),
    "Перекрытие Лондон–Нью-Йорк": (time(hour=16, minute=30), "🔁 Перекрытие Лондон–Нью-Йорк началось.")
}

user_jobs = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text("Бот запущен. Я буду напоминать о начале торговых сессий.")

    for session_name, (session_time, message) in SESSIONS.items():
        job = context.job_queue.run_daily(
            send_message,
            time=session_time,
            context={'chat_id': chat_id, 'message': message},
            name=f"{session_name}_{chat_id}"
        )
        user_jobs.setdefault(chat_id, []).append(job)

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    jobs = user_jobs.get(chat_id, [])
    for job in jobs:
        job.schedule_removal()
    user_jobs[chat_id] = []
    await update.message.reply_text("Уведомления остановлены.")

async def send_message(context: ContextTypes.DEFAULT_TYPE):
    job_data = context.job.context
    await context.bot.send_message(chat_id=job_data['chat_id'], text=job_data['message'])

def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))
    application.run_polling()

if __name__ == '__main__':
    main()
