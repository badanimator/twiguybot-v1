
from telegram import Update
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from fastapi import FastAPI, Request, HTTPException, Query, Header
from fastapi.responses import JSONResponse
from poster import post_to_telegram
from models import Content, ChannelSubscription
from telegram.ext import CommandHandler, CallbackQueryHandler
from db import SessionLocal, create_db_and_tables
from utils import fetch_reddit_posts
from bot import (
    subscribe, unsubscribe,
    category_selected,
    telegram_app
)
from config import Config


app = FastAPI(title="Telegram Bot")


telegram_app.add_handler(CommandHandler("subscribe", subscribe))
telegram_app.add_handler(CommandHandler("unsubscribe", unsubscribe))
telegram_app.add_handler(CallbackQueryHandler(category_selected))

@app.on_event("startup")
async def on_startup():
    create_db_and_tables()

    webhook_url = f"{Config.WEBHOOK_URL}/webhook"
    await telegram_app.bot.set_webhook(url=webhook_url)
    print(f"✅ Webhook set to {webhook_url}")

    await telegram_app.initialize()
    await telegram_app.start()

@app.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle Telegram updates via webhook"""
    data = await request.json()
    update = Update.de_json(data, telegram_app.bot)
    await telegram_app.process_update(update)
    return {"status": "ok"}

@app.get("/")
def list_content(
    x_api_key: str = Header(None),
    posted: bool | None = Query(None, description="Filter by posted status"),
):
    if x_api_key != Config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    session = SessionLocal()
    try:
        query = session.query(Content)
        if posted is not None:
            query = query.filter(Content.posted == posted)

        contents = query.order_by(Content.priority.desc(), Content.fetched_at.desc()).all()
        return [c.to_dict() for c in contents]
    finally:
        session.close()

@app.get("/subscriptions")
def list_subscriptions(request: Request, x_api_key: str = Header(None), limit: int = Query(10)):
    if x_api_key != Config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    session = SessionLocal()

    try:
        subs = session.query(ChannelSubscription).limit(limit).all()
        return [s.to_dict() for s in subs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e.args}")
    finally:
        session.close()

@app.post("/post-now")
async def post_now(request: Request, x_api_key: str = Header(None), limit: int = Query(10)):
    # --- Verify API Key ---
    if x_api_key != Config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    session = SessionLocal()

    unposted = (
        session.query(Content)
        .filter(Content.posted == False)
        .order_by(Content.priority.desc(), Content.fetched_at.asc())
        .limit(limit)
        .offset(0)
        .first()
    )

    # --- Get content ---
    if not unposted:
        return JSONResponse(content={"message": "No unposted content found."}, status_code=200)

    # --- Post to Telegram asynchronously ---
    await post_to_telegram(unposted.id)

    return {"status": "queued", "type": unposted.type}

@app.post("/fetch/football-trolls")
async def troll_football_reddit(x_api_key: str = Header(None)):
    """Fetch football memes from Reddit and save them."""
    if x_api_key != Config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    session = SessionLocal()

    try:
        posts = fetch_reddit_posts("soccercirclejerk", 20)
        saved_posts = 0

        for data in posts:
            content = Content(
                source_id=data["source_id"],
                source=data["source"],
                category=data["category"],
                title=data["title"][:480],
                url=data["url"],
                type=data["type"],
                fetched_at=datetime.now()
            )

            try:
                session.add(content)
                session.commit()
                saved_posts += 1
            except IntegrityError:
                session.rollback()
                continue  # skip duplicates

        return {
            "status": "success",
            "message": f"{saved_posts} new posts fetched (images, videos, and text).",
        }

    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=500, detail=f"Error fetching data: {e}")

    finally:
        session.close()

# --- Run locally ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("routes:app", port=5000, reload=True)
