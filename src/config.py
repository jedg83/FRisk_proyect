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
    "https://feeds.reuters.com/Reuters/worldNews",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://www.theguardian.com/world/financial-crime/rss",
    "https://fcpablog.com/feed/",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.feedburner.com/AssociatedPress/WorldNews",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://rss.dw.com/rdf/rss-en-top",
    "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
    "https://www.worldbank.org/en/news/all?format=rss",
    "https://www.imf.org/en/News/Articles?format=rss",
    "https://news.google.com/rss/",
    "https://news.google.com/rss/search?q=corruption&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=anti+money+laundering&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=terrorist+financing&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss?hl=es&gl=ES&ceid=ES:es",
    "https://news.google.com/rss?hl=it&gl=IT&ceid=IT:it",
]
