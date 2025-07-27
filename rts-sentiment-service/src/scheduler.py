# scheduler.py
import schedule
import threading
import time
from services.crawler import crawl_from_sources
from services.sentiment import analyze_sentiment
from config import mongo_client

def scheduled_crawl():
    print("[Scheduler] Running...")
    db = mongo_client["news_db"]
    collection = db["articles"]
    articles = crawl_from_sources()

    for article in articles:
        if not collection.find_one({"title": article["title"]}):
            article["sentiment"] = analyze_sentiment(article["title"])
            collection.insert_one(article)

def run_scheduler():
    schedule.every(1).hours.do(scheduled_crawl)
    while True:
        schedule.run_pending()
        time.sleep(1)
