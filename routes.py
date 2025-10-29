import requests
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from fastapi import FastAPI, Request, HTTPException, Query, Header
from fastapi.responses import JSONResponse
from poster import post_to_telegram
from config import Config
from models import Content, TypeConst, SourceConst
from db import SessionLocal, create_db_and_tables
from utils import fetch_reddit_posts


app = FastAPI(title="Telegram Meme Bot")
db = SessionLocal()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

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


@app.post("/post-now")
async def post_now(request: Request, x_api_key: str = Header(None), type: str = Query(None)):
    # --- Verify API Key ---
    if x_api_key != Config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    
    unposted = (
        db.query(Content)
        .filter(Content.posted == False)
        .order_by(Content.priority.desc(), Content.fetched_at.asc())
        .limit(10)
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
