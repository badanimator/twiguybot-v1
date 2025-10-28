import random
import requests

def get_random_meme():
    try:
        r = requests.get("https://meme-api.com/gimme", timeout=10)
        data = r.json()
        return {
            "type": "meme",
            "title": data["title"],
            "image_url": data["url"],
            "source": data["postLink"],
        }
    except Exception as e:
        print("Error fetching meme:", e)
        return None


def get_random_quote():
    try:
        r = requests.get("https://zenquotes.io/api/random", timeout=10)
        data = r.json()[0]
        return {"type": "quote", "text": f"“{data['q']}”\n– *{data['a']}*"}
    except Exception as e:
        print("Error fetching quote:", e)
        return None


def get_random_joke():
    try:
        r = requests.get("https://v2.jokeapi.dev/joke/Any", timeout=10)
        data = r.json()
        if data["type"] == "single":
            text = data["joke"]
        else:
            text = f"{data['setup']}\n\n{data['delivery']}"
        return {"type": "joke", "text": text}
    except Exception as e:
        print("Error fetching joke:", e)
        return None


def get_content(content_type=None):
    content_type = (content_type or "").lower()
    if content_type == "meme":
        return get_random_meme()
    elif content_type == "quote":
        return get_random_quote()
    elif content_type == "joke":
        return get_random_joke()
    else:
        return random.choice([get_random_meme, get_random_quote, get_random_joke])()