"""
Anonymous Telegram Bot
Author: Ali
Description:
A Telegram bot that allows users to send messages anonymously to the bot owner.
The owner can view user info, reply privately, and manage conversations.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from keep_alive import keep_alive  # optional: keeps the bot running 24/7

# ================= CONFIG =================
BOT_TOKEN = "YOUR_BOT_TOKEN"        # Replace with your bot token
OWNER_ID = YOUR_TELEGRAM_ID         # Replace with your Telegram ID
WELCOME_STICKER = "https://media.giphy.com/media/v1.Y2lkPTc5MGI3NjExdGE1N2lsZmY3M25ucXJsdWgweWlmZGNlZXhyN3gwc2F3YzU5ajNxNyZlcD12MV9zdGlja2Vyc19zZWFyY2gmY3Q9cw/gCxd0kUSR6I9dflWgm/giphy.gif"
# =========================================

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Runtime state to track replies
state = {
    "active_user_for_reply": {},  # OWNER_ID -> target user ID
    "replying": {},               # OWNER_ID -> True/False
}

def user_summary(user) -> str:
    """
    Returns a formatted string with user information.
    """
    name = user.full_name or "No Name"
    uid = user.id
    username = f"@{user.username}" if user.username else "-"
    return f"🔹 Name: {name}\n🔹 ID: <code>{uid}</code>\n🔹 Username: {username}"

# ================= Handlers =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles /start command for users.
    Sends welcome message and notifies the owner.
    """
    msg = update.effective_message
    user = update.effective_user

    await msg.reply_text("👋 Hello! You can send messages anonymously to the owner.")

    if WELCOME_STICKER:
        try:
            await msg.reply_sticker(WELCOME_STICKER)
        except Exception:
            pass

    # Notify owner
    text = "💌 A user started the bot."
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("📇 Info", callback_data=f"info_{user.id}")],
        [InlineKeyboardButton("💬 Reply", callback_data=f"reply_{user.id}")]
    ])
    try:
        await context.bot.send_message(chat_id=OWNER_ID, text=text, reply_markup=keyboard)
    except Exception as e:
        logger.exception("Failed to notify owner: %s", e)

# ----- Callback handlers -----
async def callback_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows user information to the owner."""
    query = update.callback_query
    await query.answer()
    try:
        target_id = int(query.data.split("_", 1)[1])
        user = await context.bot.get_chat(target_id)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data=f"back_{target_id}")]])
        await query.edit_message_text(user_summary(user), parse_mode="html", reply_markup=keyboard)
    except Exception as e:
        await query.edit_message_text("❌ Failed to fetch user info.")
        logger.exception("callback_info error: %s", e)

async def callback_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Back button handler to return to main menu."""
    query = update.callback_query
    await query.answer()
    try:
        target_id = int(query.data.split("_", 1)[1])
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📇 Info", callback_data=f"info_{target_id}")],
            [InlineKeyboardButton("💬 Reply", callback_data=f"reply_{target_id}")]
        ])
        await query.edit_message_text("💌 A user started the bot.", reply_markup=keyboard)
    except Exception as e:
        logger.exception("callback_back error: %s", e)

async def callback_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Prepares the bot owner to reply to a user."""
    query = update.callback_query
    await query.answer()
    target_id = int(query.data.split("_", 1)[1])
    state["active_user_for_reply"][OWNER_ID] = target_id
    state["replying"][OWNER_ID] = True
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("❌ Cancel", callback_data="cancel_reply")]])
    await query.edit_message_text("💬 You are now replying. Please send your message.", reply_markup=keyboard)

async def callback_cancel_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels the current reply session."""
    query = update.callback_query
    await query.answer()
    state["replying"].pop(OWNER_ID, None)
    state["active_user_for_reply"].pop(OWNER_ID, None)
    await query.edit_message_text("⛔️ Reply cancelled.")

async def relay_any(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Relays messages:
    - User → Owner
    - Owner → User if replying
    """
    msg = update.effective_message
    sender = update.effective_user

    # Owner replying to user
    if sender.id == OWNER_ID and state["replying"].get(OWNER_ID):
        target_id = state["active_user_for_reply"].get(OWNER_ID)
        if not target_id:
            await msg.reply_text("❌ No target user selected.")
            return
        try:
            await context.bot.copy_message(chat_id=target_id, from_chat_id=OWNER_ID, message_id=msg.message_id)
            await msg.reply_text("✅ Message sent.")
        except Exception as e:
            await msg.reply_text("❌ Failed to send message.")
            logger.exception("Owner->User error: %s", e)
        state["replying"].pop(OWNER_ID, None)
        state["active_user_for_reply"].pop(OWNER_ID, None)
        return

    # User sending message to owner
    if sender.id != OWNER_ID:
        try:
            header = f"📨 Message from user:"
            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("📇 Info", callback_data=f"info_{sender.id}")],
                [InlineKeyboardButton("💬 Reply", callback_data=f"reply_{sender.id}")]
            ])
            await context.bot.send_message(chat_id=OWNER_ID, text=header, parse_mode="html", reply_markup=keyboard)
            await context.bot.copy_message(chat_id=OWNER_ID, from_chat_id=sender.id, message_id=msg.message_id)
        except Exception as e:
            logger.exception("Failed to forward to owner: %s", e)

# ================= MAIN =================

def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN":
        print("Set BOT_TOKEN before running.")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Command handler
    app.add_handler(CommandHandler("start", start))

    # Callback handlers
    app.add_handler(CallbackQueryHandler(callback_info, pattern=r"^info_"))
    app.add_handler(CallbackQueryHandler(callback_back, pattern=r"^back_"))
    app.add_handler(CallbackQueryHandler(callback_reply, pattern=r"^reply_"))
    app.add_handler(CallbackQueryHandler(callback_cancel_reply, pattern=r"^cancel_reply$"))

    # Message relay
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, relay_any))

    logger.info("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    keep_alive()  # optional: keep bot alive 24/7
    main()
