import requests
import time
from fastapi import HTTPException

def fetch_reddit_posts(subreddit: str = "soccercirclejerk", limit: int = 20):
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
    headers = {
        "User-Agent": "MyRedditFetcher/1.0 (by u/Sa_Dorf)",
        "Accept": "application/json",
    }

    for attempt in range(3):  # retry 3 times on failure
        try:
            r = requests.get(url, headers=headers, timeout=10)
            
            # Handle non-200 responses gracefully
            if r.status_code != 200:
                print(f"⚠️ Reddit returned {r.status_code}: {r.text[:200]}")
                time.sleep(2 ** attempt)
                continue

            # Ensure the content is JSON
            if not r.headers.get("content-type", "").startswith("application/json"):
                print(f"⚠️ Non-JSON response detected:\n{r.text[:300]}")
                raise HTTPException(
                    status_code=502,
                    detail="Reddit returned HTML or blocked request (Cloudflare).",
                )

            data = r.json()
            posts = data.get("data", {}).get("children", [])
            return posts

        except requests.RequestException as e:
            print(f"⚠️ Network error: {e}")
            time.sleep(2 ** attempt)
        except ValueError:
            print(f"⚠️ JSON decode error:\n{r.text[:300]}")
            time.sleep(2 ** attempt)

    raise HTTPException(status_code=500, detail="Error fetching data from Reddit")
