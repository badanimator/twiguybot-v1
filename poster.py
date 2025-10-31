import re
from telegram import Bot
from datetime import datetime
from telegram.constants import ParseMode

from config import Config
from models import Content, TypeConst
from db import SessionLocal
from utils import download_video

bot = Bot(token=Config.BOT_TOKEN)


def escape_markdown(text: str) -> str:
    """
    Escape special MarkdownV2 characters for Telegram safely.
    """
    if not text:
        return ""
    # Escape Telegram MarkdownV2 reserved characters
    escape_chars = r"_*[]()~`>#+-=|{}.!"
    text = re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

    # Fix unmatched brackets (a common Reddit title issue)
    # Removes trailing unmatched "[" or "]"
    text = text.replace("\\[", "[").replace("\\]", "]")
    if text.count("[") != text.count("]"):
        text = re.sub(r"[\[\]]", "", text)
    return text


async def post_to_telegram(content_id: int):
    session = SessionLocal()
    try:
        content = session.get(Content, content_id)
        if not content:
            return {"error": "Content not found"}

        title = escape_markdown(content.title or "")
        url = content.url or ""
        message_caption = f"{title}\n\n[Source]({escape_markdown(content.source)})" if content.source else title

        if content.type == TypeConst.IMAGE.value:
            await bot.send_photo(
                chat_id=Config.CHANNEL_ID,
                photo=url,
                caption=message_caption,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        elif content.type == TypeConst.VIDEO.value:
            video_data = download_video(url)

            await bot.send_video(
                chat_id=Config.CHANNEL_ID,
                video=video_data,
                caption=message_caption,
                parse_mode=ParseMode.MARKDOWN_V2,
            )
        else:
            await bot.send_message(
                chat_id=Config.CHANNEL_ID,
                text=f"{message_caption}\n\n{escape_markdown(url)}",
                parse_mode=ParseMode.MARKDOWN_V2,
            )

        print(f"✅ Posted content ID {content.id} ({content.type}) successfully.")
        return {"status": "success"}

    except Exception as e:
        session.rollback()
        print(f"⚠️ Telegram send error: {e}")
        return {"status": "error", "error": str(e)}
    finally:
        # ✅ Mark as posted
        content.posted = True
        content.posted_at = datetime.now()
        session.commit()
        session.close()
