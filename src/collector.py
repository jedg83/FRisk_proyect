import feedparser
import json
import os
from datetime import datetime
from dateutil import parser as date_parser
from src import config

# ✅ Keywords related to AML (Anti-Money Laundering), TF (Terrorism Financing), and corruption
KEYWORDS = [
    "money laundering",
    "terrorist financing",
    "terrorism financing",
    "terrorism",
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
    "corruption",
    "crime",
    "illegal finance",
]

# ✅ Store last processed dates so we only pull *new* articles
STATE_FILE = "data/feed_state.json"


# --- Helpers -------------------------------------------------------------

def load_feed_state():
    """Load the last processed date for each feed (if available)."""
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}


def save_feed_state(state):
    """Save the latest processed date for each feed."""
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)


def parse_date(entry):
    """Try multiple ways to extract or parse the article publication date."""
    # RSS structured fields
    for field in ["published_parsed", "updated_parsed"]:
        if hasattr(entry, field) and getattr(entry, field):
            try:
                return datetime(*getattr(entry, field)[:6])
            except Exception:
                pass

    # ISO-style or textual date strings
    for field in ["published", "updated"]:
        date_str = entry.get(field)
        if date_str:
            try:
                return date_parser.parse(date_str)
            except Exception:
                pass

    return None


# --- Main collector ------------------------------------------------------

def collect_news():
    """Fetch and filter AML/TF/Corruption news from multiple RSS sources."""
    feed_state = load_feed_state()
    new_feed_state = feed_state.copy()
    all_news = []

    for feed_url in config.RSS_FEEDS:
        print(f"\n📡 Fetching: {feed_url}")

        try:
            feed = feedparser.parse(feed_url)
            source_title = feed.feed.get("title", feed_url)
            entries = feed.entries
            print(f"📥 Retrieved {len(entries)} entries from {source_title}")

            if not entries:
                print(f"⚠️ No entries found in {feed_url}")
                continue

            # Get the last processed date for this feed
            last_date_str = feed_state.get(feed_url)
            last_date = datetime.fromisoformat(last_date_str) if last_date_str else None
            newest_date = last_date

            for entry in entries:
                published_date = parse_date(entry)
                if not published_date:
                    # Use current date as fallback (helps for feeds missing dates)
                    published_date = datetime.utcnow()

                # Skip entries already processed
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
                    print(f"📰 Match found: {title[:80]}...")

                    # Update newest date seen
                    if not newest_date or published_date > newest_date:
                        newest_date = published_date
                else:
                    # Uncomment to debug skipped items:
                    # print(f"⏭️ Skipped (no keyword): {title}")
                    pass

            # Update feed state
            if newest_date:
                new_feed_state[feed_url] = newest_date.isoformat()

        except Exception as e:
            print(f"❌ Error parsing feed {feed_url}: {e}")

    # Save the updated feed state
    save_feed_state(new_feed_state)

    print(f"\n✅ Collected {len(all_news)} new AML/TF/Corruption-related articles from {len(config.RSS_FEEDS)} feeds.\n")
    return all_news