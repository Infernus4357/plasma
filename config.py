import os


BOT_TOKEN = os.environ["BOT_TOKEN"]

DATABASE_URI = os.environ["DATABASE_URI"]
DATABASE_NAME = os.environ["DATABASE_NAME"]

REDIS_URI = os.environ["REDIS_URI"]
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")
