from pymongo import MongoClient
BOT_NAME = "scrapy_crawlers"
SPIDER_MODULES = ["scrapy_crawlers.spiders"]
NEWSPIDER_MODULE = "scrapy_crawlers.spiders"
MONGO_URI = "mongodb+srv://pdkhoi22:G8UHACDROSDJ7BKG@cluster0.pupyf.mongodb.net/"
DB_NAME = "news_app"
COLLECTION_NAME = "news"
mongo_client = MongoClient(MONGO_URI)
ROBOTSTXT_OBEY = True

ITEM_PIPELINES = {
    'scrapy_crawlers.pipelines.MongoPipeline': 300,
}
