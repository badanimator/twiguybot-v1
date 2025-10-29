import praw
from config import Config

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

