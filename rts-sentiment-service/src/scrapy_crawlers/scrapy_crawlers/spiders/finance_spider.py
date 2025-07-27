import scrapy
from datetime import datetime
from scrapy_crawlers.items import FinanceArticleItem

FINANCE_KEYWORDS = [
    "tài chính", "chứng khoán", "lãi suất", "ngân hàng", "lạm phát",
    "đầu tư", "thị trường", "USD", "VND", "vàng", "giá dầu",
    "trái phiếu", "cổ phiếu", "tỷ giá", "kinh tế", "doanh nghiệp",
    "lợi nhuận", "doanh thu", "phát hành", "IPO", "niêm yết",
    "quỹ đầu tư", "thanh khoản", "giảm phát", "vốn hóa", "FED", "lãi vay",
    "bitcoin", "ethereum", "crypto", "tiền số", "tiền điện tử",
    "blockchain", "defi", "web3", "altcoin", "binance"
]

def contains_finance_keyword(title, content):
    combined = (title + " " + content).lower()
    return any(keyword in combined for keyword in FINANCE_KEYWORDS)


class FinanceSpider(scrapy.Spider):
    name = "finance_spider"
    allowed_domains = ["vnexpress.net", "cafef.vn", "baodautu.vn", "vietnamfinance.vn"]
    start_urls = [
        "https://vnexpress.net/kinh-doanh",
        "https://cafef.vn/thi-truong-chung-khoan.chn",
        "https://baodautu.vn/chung-khoan/",
        "https://vietnamfinance.vn/tai-chinh.htm"
    ]

    custom_settings = {
        "DEFAULT_REQUEST_HEADERS": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        },
        "DOWNLOAD_DELAY": 1,
        "RETRY_TIMES": 3,
        "CONCURRENT_REQUESTS": 2
    }

    def parse(self, response):
        print(f"\n🔎 Đang parse URL: {response.url}")

        # VNExpress
        if "vnexpress.net" in response.url:
            links = response.css("h3.title-news a[href]::attr(href)").getall()[:10]
            print(f"➡️ VNExpress: {len(links)} link")
            for link in links:
                yield response.follow(link, callback=self.parse_article, meta={"source": "VNExpress"})

        # CafeF
        elif "cafef.vn" in response.url:
            links = response.css("h3 a::attr(href)").getall()[:10]
            print(f"➡️ CafeF: {len(links)} link")
            for link in links:
                yield response.follow(link, callback=self.parse_article, meta={"source": "CafeF"})

        # Báo Đầu Tư
        elif "baodautu.vn" in response.url:
            links = response.css("h3 a::attr(href)").getall()[:10]
            print(f"➡️ Báo Đầu tư: {len(links)} link")
            for link in links:
                yield response.follow(link, callback=self.parse_article, meta={"source": "Báo Đầu Tư"})

        # VietnamFinance
        elif "vietnamfinance.vn" in response.url:
            links = response.css("h3 a::attr(href)").getall()[:10]
            print(f"➡️ VietnamFinance: {len(links)} link")
            for link in links:
                yield response.follow(link, callback=self.parse_article, meta={"source": "VietnamFinance"})

    def parse_article(self, response):
        title = response.css("title::text").get(default="").strip()
        content = " ".join([p.strip() for p in response.css("p::text").getall() if p.strip()])

        print(f"\n📰 Đang parse: {title[:80]}...")

        if contains_finance_keyword(title, content):
            item = FinanceArticleItem()
            item["source"] = response.meta["source"]
            item["title"] = title
            item["link"] = response.url
            item["content_full"] = content
            item["published_at"] = datetime.utcnow()
            print(f"✅ [OK] Lưu bài: {title}")
            yield item
        else:
            print(f"❌ [BỎ] Không có từ khóa: {title}")
