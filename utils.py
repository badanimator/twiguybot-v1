import praw
from config import Config
import requests
from io import BytesIO

reddit = praw.Reddit(
    client_id=Config.REDDIT_CLIENT_ID,
    client_secret=Config.REDDIT_CLIENT_SECRET,
    user_agent=Config.REDDIT_USER_AGENT,
)

def fetch_reddit_posts(subreddit: str = "soccercirclejerk", limit: int = 20):
    """Fetch recent trending Reddit posts."""
    posts = []
    for submission in reddit.subreddit(subreddit).hot(limit=limit):
        # Skip stickied/mod posts
        if submission.stickied:
            continue

        post_type = (
            "video" if submission.is_video else
            "image" if any(submission.url.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".gif"]) else
            "text"
        )

        posts.append({
            "source_id": submission.id,
            "source": "reddit",
            "title": submission.title,
            "url": submission.url,
            "type": post_type,
        })

    return posts

def download_video(url: str):
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        video_data = BytesIO(response.content)
        video_data.name = "video.mp4"
        return video_data
    except Exception as e:
        print(f"⚠️ Error downloading video: {e}")
        return None
