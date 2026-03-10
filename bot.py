import re
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from config import BOT_TOKEN, SOURCE_CHAT_ID, TOPIC_ID

total_sum = 0.0

def parse_sum(text: str):
    match = re.search(r"Sum:\s*([\d]+[.,]\d+|\d+)", text, re.IGNORECASE)
    if match:
        return float(match.group(1).replace(",", "."))
    return None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global total_sum
    message = update.message
    if not message or not message.text:
        return
    if message.chat_id != SOURCE_CHAT_ID:
        return
    if message.message_thread_id != TOPIC_ID:
        return
    amount = parse_sum(message.text)
    if amount is None:
        return
    total_sum += amount
    await message.reply_text(
        f"➕ Добавлено: {amount:.2f}\n"
        f"📊 Итого: {total_sum:.2f}",
        message_thread_id=TOPIC_ID
    )

async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global total_sum
    if not update.message:
        return
    total_sum = 0.0
    await update.message.reply_text("✅ Сумма сброшена до 0.")

async def set_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global total_sum
    if not update.message:
        return
    if not context.args:
        await update.message.reply_text("Использование: /set 100,50")
        return
    try:
        value = float(context.args[0].replace(",", "."))
        total_sum = value
        await update.message.reply_text(f"✅ Сумма установлена: {total_sum:.2f}")
    except ValueError:
        await update.message.reply_text("❌ Неверный формат. Пример: /set 100,50")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("set", set_command))
    print("Бот запущен...")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
