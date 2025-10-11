import feedparser
from gnews import GNews
from src import config


# Define keywords to focus only on AML, TF, and corruption-related topics
KEYWORDS = [
    "money laundering",
    "terrorist financing",
    "terrorism financing",
    "corruption",
    "bribery",
    "fraud",
    "embezzlement",
    "sanctions",
    "tax evasion",
    "organized crime",
    "illicit finance",
    "financial crime",
    "shell companies",
    "offshore accounts",
    "kleptocracy",
    "foreign bribery",
]

def collect_news():
    """
    Collects and filters AML/TF/corruption-related news
    from multiple international RSS sources defined in config.py.
    """
    all_news = []

    for feed_url in config.RSS_FEEDS:
        print(f"📡 Fetching: {feed_url}")
        try:
            feed = feedparser.parse(feed_url)

            if not feed.entries:
                print(f"⚠️  No entries found in {feed_url}")
                continue

            source_title = feed.feed.get("title", feed_url)

            for entry in feed.entries:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")
                published = entry.get("published", "")

                # Combine title + summary for keyword search
                combined_text = f"{title} {summary}".lower()

                if any(keyword.lower() in combined_text for keyword in KEYWORDS):
                    all_news.append({
                        "title": title,
                        "summary": summary,
                        "link": link,
                        "published": published,
                        "source": source_title
                    })

        except Exception as e:
            print(f"❌ Error parsing feed {feed_url}: {e}")

    print(f"✅ Collected {len(all_news)} relevant articles from {len(config.RSS_FEEDS)} feeds.")
    return all_news
