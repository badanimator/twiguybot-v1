import os

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8358721757:AAGJBleg1qmwmjeP08NNjIz_VCXNCLtagaE")
    CHANNEL_ID = os.getenv("CHANNEL_ID", "@twiguy")
    API_KEY = os.getenv("API_KEY", "supersecretapikey")
    POST_INTERVAL_MINUTES:float = float(os.getenv("POST_INTERVAL_MINUTES", 1/60))
