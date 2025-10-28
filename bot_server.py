from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from content import get_content
from poster import post_to_telegram
from config import Config

app = FastAPI(title="Telegram Meme Bot")

@app.get("/")
async def index():
    return {"message": "Telegram Meme Bot running!"}

@app.api_route("/post-now", methods=["GET", "POST"])
async def post_now(request: Request, api_key: str = Query(None), type: str = Query(None)):
    # --- Verify API Key ---
    if api_key != Config.API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")

    # --- Get content ---
    content = get_content(type)
    if not content:
        return JSONResponse(content={"message": "No meme found"}, status_code=200)

    # --- Post to Telegram asynchronously ---
    await post_to_telegram(content)

    return {"status": "queued", "type": content["type"]}

# --- Run locally ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("bot_server:app", host="0.0.0.0", port=5000, reload=True)
