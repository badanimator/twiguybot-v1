from telegram import Bot, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ApplicationBuilder

from config import Config
from models import ChannelSubscription, ContentCategoryConst
from db import SessionLocal

bot = Bot(token=Config.BOT_TOKEN)
telegram_app = ApplicationBuilder().token(Config.BOT_TOKEN).build()

# Available content categories
AVAILABLE_CATEGORIES = [c.value for c in ContentCategoryConst]



async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = SessionLocal()

    try:
        # Expect: /subscribe <channel_id or @username> <category>
        if len(context.args) < 2:
            await update.message.reply_text(
                "Usage: `/subscribe <channel_id or @username> <category>`",
                parse_mode="Markdown",
            )
            return

        channel_input = context.args[0]
        category = context.args[1]

        if category not in AVAILABLE_CATEGORIES:
            await update.message.reply_text(
                f"❌ Invalid category. Choose from: {', '.join(AVAILABLE_CATEGORIES)}"
            )
            return

        # Try to get channel info via bot.get_chat
        try:
            chat = await update.get_bot().get_chat(channel_input)
            channel_id = str(chat.id)
            channel_name = chat.title or channel_input
        except Exception as e:
            await update.message.reply_text(f"⚠️ Could not access channel: {e}")
            return

        # Check if already subscribed
        existing = (
            session.query(ChannelSubscription)
            .filter_by(channel_id=channel_id, category=category)
            .first()
        )
        if existing:
            await update.message.reply_text(f"✅ Channel already subscribed to *{category}*.", parse_mode="Markdown")
            return

        # Add new subscription
        sub = ChannelSubscription(channel_id=channel_id, channel_name=channel_name, category=category)
        session.add(sub)
        session.commit()

        await update.message.reply_text(f"🎉 Subscribed *{channel_name}* to *{category}*!", parse_mode="Markdown")

    finally:
        session.close()

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    session = SessionLocal()
    chat_id = str(update.effective_chat.id)
    try:
        if not context.args:
            await update.message.reply_text("Usage: `/unsubscribe <category>`", parse_mode="Markdown")
            return

        category = context.args[0]
        sub = (
            session.query(ChannelSubscription)
            .filter_by(channel_id=chat_id, category=category)
            .first()
        )

        if not sub:
            await update.message.reply_text(f"You're not subscribed to *{category}*.", parse_mode="Markdown")
            return

        session.delete(sub)
        session.commit()
        await update.message.reply_text(f"🛑 Unsubscribed from *{category}*.", parse_mode="Markdown")

    finally:
        session.close()


# Callback handler for button clicks (inline keyboard)
async def category_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    session = SessionLocal()
    try:
        chat = query.message.chat
        chat_id = str(chat.id)
        chat_name = chat.title or chat.username or "Unnamed"

        # Extract category name from callback data
        _, category = query.data.split(":", 1)

        existing = (
            session.query(ChannelSubscription)
            .filter_by(channel_id=chat_id, category=category)
            .first()
        )
        if existing:
            await query.edit_message_text(f"✅ Already subscribed to *{category}*.", parse_mode="Markdown")
            return

        sub = ChannelSubscription(channel_id=chat_id, channel_name=chat_name, category=category)
        session.add(sub)
        session.commit()

        await query.edit_message_text(f"🎉 Subscribed successfully to *{category}*!", parse_mode="Markdown")

    finally:
        session.close()

