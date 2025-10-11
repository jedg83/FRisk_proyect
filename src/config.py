# Configuration for your AI News Agent
from datetime import date
LANGUAGE = "en"
MAX_RESULTS = 20
TOPICS = ["money laundering", "terrorist financing", "corruption"]
OUTPUT_FILE = f"data/news_intelligence_{date.today()}.json"
RSS_FEEDS = [
    "https://www.fatf-gafi.org/en/rss.xml",
    "https://www.transparency.org/en/rss",
    "https://www.occrp.org/en/rss",
    "https://www.europol.europa.eu/media-press/newsroom/rss.xml",
    "https://www.interpol.int/en/News-and-Events/News/rss",
    "https://feeds.reuters.com/reuters/crimeNews",
    "https://www.theguardian.com/world/financial-crime/rss",
    "https://fcpablog.com/feed/",
    "https://news.google.com/rss/",
]
