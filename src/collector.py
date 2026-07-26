import feedparser
import json
import os
import re
from datetime import datetime, timezone
from dateutil import parser as date_parser
from src import config
from langdetect import detect, DetectorFactory


DetectorFactory.seed = 0  # For consistent language detection results

# Load English and multilingual NLP models when available.
# The project should still work even if spaCy is not installed or the model is unavailable.
try:
    import spacy
except ImportError:  # pragma: no cover - optional dependency
    spacy = None

nlp = None
if spacy is not None:
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        try:
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=False)
        except Exception:
            pass
        try:
            nlp = spacy.load("en_core_web_sm")
        except Exception:
            nlp = None



# Keywords related to AML (Anti-Money Laundering), TF (Terrorism Financing), corruption,
# and broader criminal activity involving financial gain
KEYWORDS = [
    # Financial crimes
    "money laundering",
    "lavado de activos",
    "lavado de dinero",
    "terrorist financing",
    "terrorism financing",
    "financiamiento del terrorismo",
    "terrorism",
    "bribery",
    "fraud",
    "fraude",
    "embezzlement",
    "sanctions",
    "tax evasion",
    "illicit finance",
    "financial crime",
    "shell companies",
    "offshore accounts",
    "kleptocracy",
    "foreign bribery",
    "corruption",
    "corrupción",
    "anticorrupción",
    "AML",
    "TF",

    # Organized crime
    "organized crime",
    "cartel",
    "drug trafficking",
    "narcotics",
    "narcotráfico",
    "human trafficking",
    "trata de personas",
    "smuggling",
    "contrabando",

    # Violent crimes with financial motives
    "kidnapping",
    "secuestro",
    "ransom",
    "rescate",
    "extortion",
    "extorsión",
    "murder for hire",
    "contract killing",
    "assassination",
    "asesinato",

    # Property crimes
    "robbery",
    "robo",
    "theft",
    "burglary",
    "heist",
    "stolen",
    "robado",

    # Italian (for Italian feeds)
    "antiriciclaggio",
    "corruzione",
    "riciclaggio",
    "finanziamento del terrorismo",
    "rapimento",
    "furto",
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

    print(f"\n✅ Collected {len(all_news)} new crime-related articles (AML/TF/Corruption/Organized Crime) from {len(config.RSS_FEEDS)} feeds.\n")
    return all_news

def is_relevant_news(title, summary):
    """Check if the article is relevant to AML, TF, corruption, or other financial crimes."""
    text = f"{title} {summary}".lower()

    # Define strong multi-language patterns
    patterns = [
        # Financial crimes
        r"\banti[- ]?money[- ]?laundering\b",
        r"\blavado de (dinero|activos)\b",
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
        r"\bmalversaci[oó]n\b",
        r"\bembezzlement\b",
        r"\btax evasion\b",

        # Organized crime
        r"\borganized crime\b",
        r"\bcartel\b",
        r"\bdrug trafficking\b",
        r"\bnarcotr[aá]fico\b",
        r"\bhuman trafficking\b",
        r"\btrata de personas\b",
        r"\bsmuggling\b",
        r"\bcontrabando\b",

        # Violent crimes with financial motives
        r"\bkidnapping\b",
        r"\bsecuestro\b",
        r"\bransom\b",
        r"\brescate\b",
        r"\bextortion\b",
        r"\bextorsi[oó]n\b",
        r"\bmurder for hire\b",
        r"\bcontract killing\b",
        r"\bassassination\b",

        # Property crimes
        r"\brobbery\b",
        r"\brobo\b",
        r"\bheist\b",
        r"\bburglary\b",
        r"\btheft\b",

        # General criminal indicators
        r"\bcriminals\b",
        r"\bcriminales\b",
        r"\billicit\b",
        r"\bil[ií]cito\b"
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
    """Extract names, orgs, and countries from the text using spaCy when available."""
    if not text:
        return [], [], []

    if nlp is not None:
        try:
            doc = nlp(text)
            people = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
            orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
            locations = [ent.text for ent in doc.ents if ent.label_ in ("GPE", "LOC")]

            # Clean organization names (remove leading articles)
            orgs_cleaned = []
            for org in orgs:
                cleaned = re.sub(r'^(the|a|an)\s+', '', org, flags=re.IGNORECASE).strip()
                if cleaned:
                    orgs_cleaned.append(cleaned)

            # Deduplicate and return
            return (list(dict.fromkeys(people)),
                    list(dict.fromkeys(orgs_cleaned)),
                    list(dict.fromkeys(locations)))
        except Exception:
            pass

    # Fallback to regex-based extraction when spaCy is unavailable or fails.
    people_set = set()
    orgs_set = set()
    locations_set = set()

    # Common words/phrases that should NOT be considered person names
    stopwords = {
        "the", "and", "for", "of", "in", "on", "at", "to", "a", "an",
        "chief", "officer", "announces", "over", "public", "assistance",
        "fraud", "arrests", "administrative", "action", "cases", "may",
        "april", "june", "july", "august", "september", "october", "november",
        "december", "january", "february", "march", "monday", "tuesday",
        "wednesday", "thursday", "friday", "saturday", "sunday"
    }

    # Extract person names - USE ONLY ONE PATTERN to avoid duplicates
    # Match 2-4 capitalized words (typical person name length)
    person_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b"
    for match in re.finditer(person_pattern, text):
        candidate = match.group(1)
        words = candidate.split()

        # Filter out false positives
        if (len(words) >= 2 and  # At least 2 words for a name
            candidate.lower() not in stopwords and
            not any(word.lower() in stopwords for word in words) and
            len(candidate) < 50):  # Names shouldn't be super long
            people_set.add(candidate)

    # Extract organizations - look for known org indicators
    # Pattern 1: Words ending with company indicators
    org_indicators = r"\b([A-Z][A-Za-z\s&.]+(?:Company|Corp|Corporation|Inc|Ltd|Group|Bank|Ministry|University|Organization|Department|Agency|Bureau))\b"
    for match in re.finditer(org_indicators, text, re.IGNORECASE):
        candidate = match.group(1).strip()
        # Remove leading articles
        candidate = re.sub(r'^(the|a|an)\s+', '', candidate, flags=re.IGNORECASE).strip()
        if len(candidate) < 100 and len(candidate) > 2:  # Reasonable length
            orgs_set.add(candidate)

    # Pattern 2: Common org patterns (abbreviations, all caps)
    org_abbrev = r"\b([A-Z]{2,}(?:\s+[A-Z]{2,})*)\b"
    for match in re.finditer(org_abbrev, text):
        candidate = match.group(1)
        if (2 <= len(candidate.replace(" ", "")) <= 10 and  # Reasonable abbreviation length
            candidate not in {"US", "UK", "EU", "UN"}):  # Exclude country codes
            orgs_set.add(candidate)

    # Extract locations - expanded list of common locations
    common_locations = [
        # Countries
        "Nigeria", "United States", "United Kingdom", "China", "Russia", "Mexico",
        "Colombia", "Venezuela", "Brazil", "Argentina", "Spain", "Italy", "France",
        "Germany", "India", "Pakistan", "Afghanistan", "Iraq", "Iran", "Syria",
        # Cities
        "Lagos", "London", "New York", "Washington", "Miami", "Los Angeles",
        "Moscow", "Beijing", "Dubai", "Hong Kong", "Singapore", "Tokyo",
        "Mexico City", "Bogota", "Caracas", "Buenos Aires", "Madrid", "Rome",
        # Regions
        "Europe", "Africa", "Asia", "Middle East", "Latin America", "South America"
    ]

    for location in common_locations:
        if re.search(rf"\b{re.escape(location)}\b", text, re.IGNORECASE):
            locations_set.add(location)

    # Convert sets to lists (preserves uniqueness)
    return list(people_set), list(orgs_set), list(locations_set)

