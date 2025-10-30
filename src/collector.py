import feedparser
import json
import os
import re
import spacy
from datetime import datetime, timezone
from dateutil import parser as date_parser
from src import config
from langdetect import detect, DetectorFactory


DetectorFactory.seed = 0  # For consistent language detection results

# Load English and multilingual NLP models
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    import subprocess
    subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"])
    nlp = spacy.load("en_core_web_sm")



# Keywords related to AML (Anti-Money Laundering), TF (Terrorism Financing), and corruption
KEYWORDS = [
    "money laundering",
    "lavado de activos",
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
    "lavado de dinero", "financiamiento del terrorismo", "corrupción", "fraude",
    "money laundering", "terrorist financing", "AML", "TF", "anticorrupción",
    "antiriciclaggio", "corruzione", "riciclaggio", "finanziamento del terrorismo"
]

# Store last processed dates so we only pull *new* articles
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
        published_date = None

        try:
            feed = feedparser.parse(feed_url)
            print(f"Fetched {len(feed.entries)} total entries from feed.")
            source_title = feed.feed.get("title", feed_url)
            entries = feed.entries
            print(f"📥 Retrieved {len(entries)} entries from {source_title}")

            if not entries:
                print(f"⚠️ No entries found in {feed_url}")
                continue

            # Get the last processed date for this feed
            last_date_str = feed_state.get(feed_url)
            last_date = None

            if last_date_str:
                try:
                    last_date = datetime.fromisoformat(last_date_str.replace("Z", "+00:00"))
                except Exception:
                    pass

            newest_date = last_date

            for entry in entries:
                title = entry.get("title", "")
                summary = entry.get("summary", "")

                if not is_relevant_news(title, summary):
                    continue
                # Parse publication date
                published_date = parse_date(entry)
                if not published_date:
                    # Use current date as fallback (helps for feeds missing dates)
                    published_date = datetime.now(timezone.utc)

                # Normalize both to UTC for fair comparison
                published_date = published_date.astimezone(timezone.utc)
                last_date_utc = last_date.astimezone(timezone.utc) if last_date else None


                # Skip entries already processed
                if last_date_utc and published_date <= last_date_utc:
                    continue

                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")
                content = (entry.get("title", "") + " " + entry.get("summary", "") + " " + entry.get("description", "")).strip()
                people, orgs, locations = extract_entities(content)

                combined_text = f"{title} {summary}".lower()
                if any(keyword.lower() in combined_text for keyword in KEYWORDS):
                    all_news.append({
                        "title": title,
                        "summary": summary,
                        "link": link,
                        "published": published_date.isoformat(),
                        "source": source_title,
                        "feed_url": feed_url,
                        "language": entry.get("language") or infer_language(title + " " + summary, fallback=config.LANGUAGE),
                        "people": people,
                        "organizations": orgs,
                        "locations": locations,
                    })
                    #print(f"📰 Match found: {title[:80]}...")

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

def is_relevant_news(title, summary):
    """Check if the article is relevant to AML, TF, or corruption."""
    text = f"{title} {summary}".lower()

    # Define strong multi-language patterns
    patterns = [
        r"\banti[- ]?money[- ]?laundering\b",
        r"\blavado de dinero\b",
        r"\bterrorismo\b",
        r"\bterrorist[- ]?financing\b",
        r"\banticorrupci[oó]n\b",
        r"\bcorruption\b",
        r"\bcorruzione\b",
        r"\briciclaggio\b",
        r"\bantiriciclaggio\b",
        r"\bfraude?\b",
        r"\bfraud\b",
        r"\bbribery\b",
        r"\bsoborno\b",
        r"\bcriminals\b",
        r"\bcriminales\b",
        r"\bmalversaci[oó]n\b"
    ]

    # Stronger signal if in the title
    title_hits = sum(bool(re.search(p, title.lower())) for p in patterns)
    text_hits = sum(bool(re.search(p, text)) for p in patterns)

    # Keep only if relevant keywords appear
    if title_hits > 0:
        return True  # Strong match in title
    elif text_hits >= 2:
        return True  # Appears multiple times in body
    else:
        return False

def infer_language(text, fallback="unknown"):
    try:
        return detect(text)
    except:
        return fallback

def extract_entities(text: str):
    """Extract names, orgs, and countries from the text using spaCy."""
    if not text:
        return [], [], []

    doc = nlp(text)
    people = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    locations = [ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC")]

    return people, orgs, locations

