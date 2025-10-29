import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHANNEL_ID = os.getenv("CHANNEL_ID")
    API_KEY = os.getenv("API_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", f'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite'))
