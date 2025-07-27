import scrapy

class FinanceArticleItem(scrapy.Item):
    title = scrapy.Field()
    link = scrapy.Field() 
    source = scrapy.Field()
    published_at = scrapy.Field()
    content_full = scrapy.Field()
    sentiment = scrapy.Field()