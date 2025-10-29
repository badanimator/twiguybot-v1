import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN", "8358721757:AAGJBleg1qmwmjeP08NNjIz_VCXNCLtagaE")
    CHANNEL_ID = os.getenv("CHANNEL_ID", "@twiguy")
    API_KEY = os.getenv("API_KEY", "supersecretapikey")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", f'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite'))

    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "UOcZNPZekP4DuqrnmA1V5Q")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "DMSToHEmFBtO07IEMpbSiGuCRex2ew")
    REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "MemeFetcher/1.0 (by u/Sa_Dorf)")

