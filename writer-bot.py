import logging
from contextlib import asynccontextmanager
from http import HTTPStatus

from fastapi import FastAPI, Request, Response
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters, ConversationHandler

from credentials import writer_bot_token, public_domain_url

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# Load environment variables
TELEGRAM_BOT_TOKEN: str = writer_bot_token
WEBHOOK_DOMAIN: str = public_domain_url

# Build the Telegram Bot application
bot_builder = (
    Application.builder()
    .token(TELEGRAM_BOT_TOKEN)
    .updater(None)
    .build()
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    """ Sets the webhook for the Telegram Bot and manages its lifecycle (start/stop). """
    await bot_builder.bot.setWebhook(url=WEBHOOK_DOMAIN)
    async with bot_builder:
        await bot_builder.start()
        yield
        await bot_builder.stop()


app = FastAPI(lifespan=lifespan)


@app.post("/")
async def process_update(request: Request):
    """ Handles incoming Telegram updates and processes them with the bot. """
    message = await request.json()
    update = Update.de_json(data=message, bot=bot_builder.bot)
    await bot_builder.process_update(update)
    return Response(status_code=HTTPStatus.OK)


async def hello(update: Update):
    await update.message.reply_text(f'Hello {update.effective_user.first_name}!' + "\n"
                                    + "I am Maintenance Bot, I track siri homes monthly maintenance expense and update payment statuses.\n "
                                    + "/expense for logging association expenses.\n"
                                    + "/tankers for tankers tracking\n"
                                    + "/home_away for updating flat owners status on being at home or away\n"
                                    + "/payment for updating maintenance amount payment status of any flat\n"
                                    + "/cancel for aborting chat anytime.\n")
    return ConversationHandler.END


async def tankers(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["Tanker 1", "Tanker 2", "Tanker 3"]]

    await update.message.reply_text(
        "Hi! My name is Maintenance Bot. I will track tankers count for you."
        "Send /cancel to stop talking to me.\n\n"
        "Provide description: ",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Tanker 1 or Tanker 2?"
        ),
    )
    return 0


async def description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Tanker Description of %s: %s", user.first_name, update.message.text)
    context.user_data['tanker_description'] = update.message.text
    await update.message.reply_text(
        "Okay! Please provide the amount.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return 1


async def tanker_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Amount Spent in Rs %s: %s", user.first_name, update.message.text)
    if not update.message.text.isdigit():
        await update.message.reply_text(
            "Please enter a valid amount in numbers only.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return 2
    await update.message.reply_text(
        "Okay! I have noted down your expense. ",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    logger.info("User %s sent a message: %s", user.first_name, update.message.text)
    if update.message.text.lower() == "cancel":
        await cancel(update, context)
    else:
        await update.message.reply_text(
            "I didn't understand that. Please use /expense to log an expense or /summary for summary.",
            reply_markup=ReplyKeyboardRemove(),
        )
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    await update.message.reply_text(
        "Bye! I hope we can talk again some day.", reply_markup=ReplyKeyboardRemove()
    )
    return -1


async def track_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["Security Salary", "Phone Recharge", "Other"]]

    await update.message.reply_text(
        "Hi! I will note down expense for you. "
        "Send /cancel to stop talking to me.\n\n"
        "What is your expense description?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Security Salary or Phone Recharge?"
        ),
    )
    return 2


async def update_payments(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["G01", "202", "401"]]

    await update.message.reply_text(
        "Hi, I will update the payment status for you. "
        "Send /cancel to stop talking to me.\n\n"
        "Which flat's payment status do you want to update?",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Flat Number?"
        ),
    )
    return 3


async def expense_amount(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user = update.message.from_user
    logger.info("Amount Spent in Rs %s: %s", user.first_name, update.message.text)
    if not update.message.text.isdigit():
        await update.message.reply_text(
            "Please enter a valid amount in numbers only.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return 2
    await update.message.reply_text(
        "Okay! I have noted down your expense. ",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


async def payment_flat(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["Paid", "Pending"]]
    user = update.message.from_user
    logger.info("Payment Status for %s: %s", user.first_name, update.message.text)
    context.user_data['flat'] = update.message.text
    await update.message.reply_text(
        "Okay! Please provide the payment status (Paid/Pending).",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Paid or Pending?"
        ),
    )
    return 4


async def payment_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Okay! I have noted down the payment status. ",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


conv_handler = ConversationHandler(
    entry_points=[CommandHandler("tankers", tankers),
                  CommandHandler("expense", track_expense),
                  CommandHandler("payment", update_payments),
                  MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text)],
    states={
        0: [MessageHandler(filters.TEXT & ~filters.COMMAND, description)],
        1: [MessageHandler(filters.TEXT & ~filters.COMMAND, tanker_amount)],
        2: [MessageHandler(filters.TEXT & ~filters.COMMAND, expense_amount)],
        3: [MessageHandler(filters.TEXT & ~filters.COMMAND, payment_flat)],
        4: [MessageHandler(filters.TEXT & ~filters.COMMAND, payment_status)],
    },
    fallbacks=[CommandHandler("cancel", cancel),
               MessageHandler(filters.COMMAND, handle_text)],
)
bot_builder.add_handler(conv_handler)
bot_builder.add_handler(CommandHandler("start", hello))
