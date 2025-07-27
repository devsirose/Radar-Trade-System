import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), "scrapy_crawlers"))
os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "scrapy_crawlers.settings")

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from scrapy_crawlers.spiders.finance_spider import FinanceSpider

if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl(FinanceSpider)
    process.start()
