from flask import Flask, render_template
from routes.news import news_bp
from config import mongo_client

app = Flask(__name__)
app.register_blueprint(news_bp, url_prefix="/news")

# Route để hiển thị trang chính
@app.route("/")
def index():
    db = mongo_client["news_app"]
    collection = db["news"]
    articles = list(collection.find().sort("publishedAt", -1))  # Mới nhất lên đầu
    return render_template("index.html", articles=articles)

if __name__ == "__main__":
    app.run(debug=True)
