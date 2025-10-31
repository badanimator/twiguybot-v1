import re
import asyncio
from datetime import datetime
from telegram.constants import ParseMode
from telegram.error import TelegramError, TimedOut, NetworkError

from models import Content, TypeConst, ChannelSubscription
from db import SessionLocal
from utils import download_video
from bot import bot



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
    """
    Send content to all subscribed Telegram channels that match its category.
    """
    session = SessionLocal()
    try:
        content = session.get(Content, content_id)
        if not content:
            return {"error": "Content not found"}

        category = content.category or "general"
        subscribers = session.query(ChannelSubscription).filter_by(category=category).all()

        if not subscribers:
            print(f"⚠️ No subscribers for category: {category}")
            return {"status": "no_subscribers"}

        title = escape_markdown(content.title or "")
        url = content.url or ""
        if not url:
            print(f"⚠️ Skipping content ID {content.id}: no media URL.")
            return {"status": "no_media"}

        message_caption = (
            f"{title}\n\n[Source]({escape_markdown(content.source)})"
            if content.source else title
        )

        success_count = 0

        for sub in subscribers:
            try:
                if content.type == TypeConst.IMAGE.value:
                    await bot.send_photo(
                        chat_id=sub.channel_id,
                        photo=url,
                        caption=message_caption,
                        parse_mode=ParseMode.MARKDOWN_V2,
                    )

                elif content.type == TypeConst.VIDEO.value:
                    video_data = download_video(url)
                    if not video_data:
                        print(f"⚠️ Could not download video for {url}")
                        continue

                    await bot.send_video(
                        chat_id=sub.channel_id,
                        video=video_data,
                        caption=message_caption,
                        parse_mode=ParseMode.MARKDOWN_V2,
                    )

                else:
                    await bot.send_message(
                        chat_id=sub.channel_id,
                        text=f"{message_caption}\n\n{escape_markdown(url)}",
                        parse_mode=ParseMode.MARKDOWN_V2,
                    )

                print(f"✅ Sent to {sub.channel_name or sub.channel_id}")
                success_count += 1
                await asyncio.sleep(0.5)  # Prevent rate limits

            except (TelegramError, TimedOut, NetworkError) as e:
                print(f"⚠️ Error sending to {sub.channel_id}: {e}")


        print(f"✅ Posted content ID {content.id} ({content.type}) to {success_count}/{len(subscribers)} channels.")
        return {"status": "success", "sent_to": success_count}

    except Exception as e:
        session.rollback()
        print(f"⚠️ Unexpected error in post_to_telegram: {e}")
        return {"status": "error", "error": str(e)}

    finally:
        content.posted = True
        content.posted_at = datetime.now()
        session.commit()
        session.close()