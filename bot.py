import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import BOT_TOKEN, ADMIN_IDS
from utils import check_membership, chat_with_gpt, add_channel

pending_channel = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in ADMIN_IDS:
        keyboard = [[InlineKeyboardButton("➕ افزودن کانال", callback_data="add_channel")]]
        await update.message.reply_text("پنل ادمین:", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        if not await check_membership(user_id):
            await update.message.reply_text("برای استفاده از ربات، ابتدا عضو کانال شوید.")
            return
        await update.message.reply_text("سلام! سوالتو بپرس.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in pending_channel:
        link = update.message.text.strip()
        if link.startswith("@"):
            add_channel(link)
            del pending_channel[user_id]
            await update.message.reply_text(f"✅ کانال {link} اضافه شد.")
        else:
            await update.message.reply_text("❌ لینک باید با @ شروع شود.")
        return

    if not await check_membership(user_id):
        await update.message.reply_text("شما عضو کانال نیستید یا لفت داده‌اید. لطفاً ابتدا عضو شوید.")
        return

    response = await chat_with_gpt(update.message.text)
    await update.message.reply_text(response)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "add_channel" and user_id in ADMIN_IDS:
        pending_channel[user_id] = True
        await query.message.reply_text("لطفاً لینک کانال را با @ بفرستید:")

app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button_handler))
app.run_polling()