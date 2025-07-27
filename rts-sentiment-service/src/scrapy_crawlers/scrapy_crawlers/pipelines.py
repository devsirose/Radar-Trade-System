# news_crawler/pipelines.py

from pymongo import MongoClient
from scrapy_crawlers import settings  # import thẳng settings.py
from scrapy_crawlers.services.sentiment import analyze_sentiment


class MongoPipeline:
    def __init__(self):
        self.client = MongoClient(settings.MONGO_URI)
        self.db = self.client[settings.DB_NAME]
        self.collection = self.db[settings.COLLECTION_NAME]

    def process_item(self, item, spider):
        item["sentiment"] = analyze_sentiment(item["title"])

        if not self.collection.find_one({"title": item["title"]}):
            self.collection.insert_one(dict(item))
        return item

    def close_spider(self, spider):
         import time
         time.sleep(2)
         self.client.close()
