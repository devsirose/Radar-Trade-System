from flask import Blueprint, jsonify
import subprocess
from config import mongo_client

news_bp = Blueprint('news', __name__)
db = mongo_client["news_app"]
collection = db["news"]

@news_bp.route("/", methods=["GET"])
def crawl_news():
    result = subprocess.run(["scrapy", "crawl", "finance_spider"], cwd="scrapy_crawlers", capture_output=True, text=True)

    if result.returncode != 0:
        return jsonify({"message": "Crawler gặp lỗi", "error": result.stderr}), 500

    # Truy vấn số lượng bài viết đã thêm
    count = collection.count_documents({})
    return jsonify({"message": f"Đã crawl thành công. Tổng số bài viết: {count}."})
