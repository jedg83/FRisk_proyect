from gnews import GNews
from src import config

def collect_news():
    google_news = GNews(language=config.LANGUAGE, max_results=config.MAX_RESULTS)
    articles = []
    for topic in config.TOPICS:
        results = google_news.get_news(topic)
        for article in results:
            article["topic"] = topic
        articles.extend(results)
    return articles
