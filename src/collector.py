
from gnews import GNews
import feedparser
import json
import os
from datetime import datetime
from src import config

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

STATE_FILE = "data/feed_state.json"

def load_feed_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_feed_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)

def parse_date(entry):
    try:
        return datetime(*entry.published_parsed[:6])
    except Exception:
        return None

def collect_news():
    feed_state = load_feed_state()
    new_feed_state = feed_state.copy()
    all_news = []

    for feed_url in config.RSS_FEEDS:
        print(f"📡 Fetching: {feed_url}")
        try:
            feed = feedparser.parse(feed_url)
            source_title = feed.feed.get("title", feed_url)

            # Get last processed date for this feed
            last_date_str = feed_state.get(feed_url)
            last_date = datetime.fromisoformat(last_date_str) if last_date_str else None
            newest_date = last_date

            for entry in feed.entries:
                published_date = parse_date(entry)
                if not published_date:
                    continue

                # Skip if entry is older or same as last saved
                if last_date and published_date <= last_date:
                    continue

                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")

                combined_text = f"{title} {summary}".lower()
                if any(keyword.lower() in combined_text for keyword in KEYWORDS):
                    all_news.append({
                        "title": title,
                        "summary": summary,
                        "link": link,
                        "published": published_date.isoformat(),
                        "source": source_title
                    })

                # Track the most recent date found
                if not newest_date or published_date > newest_date:
                    newest_date = published_date

            # Update last processed date for this feed
            if newest_date:
                new_feed_state[feed_url] = newest_date.isoformat()

        except Exception as e:
            print(f"❌ Error parsing feed {feed_url}: {e}")

    # Save updated state
    save_feed_state(new_feed_state)

    print(f"✅ Collected {len(all_news)} new articles from {len(config.RSS_FEEDS)} feeds.")
    return all_news