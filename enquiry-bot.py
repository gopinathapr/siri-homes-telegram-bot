from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, filters, MessageHandler

from credentials import enquiry_bot_token

# Replace this with your actual bot token from BotFather
BOT_TOKEN = enquiry_bot_token


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Enquiry Bot! Use /expense, /tankers, or /payments to get updates.")


async def expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💰 Monthly maintenance expenses: ₹1,23,456\nMajor heads: Security, Housekeeping, Repairs")


async def tankers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🚛 Water tanker status: 5 deliveries today.\nLast delivery: 4:30 PM")


async def payments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ 87% flats have paid maintenance for June.\nPending flats: 23")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Sorry, I didn’t understand that command. Try /expense, /tankers, or /payments.")


async def check_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Enquiry Bot is up and running!")


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("expense", expense))
    app.add_handler(CommandHandler("tankers", tankers))
    app.add_handler(CommandHandler("payments", payments))

    # Catch-all for unknown commands
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))

    print("Enquiry Bot is running...")
    app.run_polling()


if __name__ == '__main__':
    main()
