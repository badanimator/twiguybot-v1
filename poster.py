from telegram import Bot
from telegram.constants import ParseMode
from config import Config

bot = Bot(token=Config.BOT_TOKEN)

async def post_to_telegram(content):
    try:
        if not content:
            return {"error": "No content found"}
        
        if content["type"] == "meme":
            await bot.send_photo(
                chat_id=Config.CHANNEL_ID,
                photo=content["image_url"],
                caption=f"{content['title']}\n\n[Source]({content['source']})",
                parse_mode=ParseMode.MARKDOWN
            )
        else:
            await bot.send_message(
                chat_id=Config.CHANNEL_ID,
                text=content["text"],
                parse_mode=ParseMode.MARKDOWN
            )
        print("✅ A post have been sent")
        return {"status": "success"}
    except Exception as e:
        return {"status": "error", "error": str(e)}
