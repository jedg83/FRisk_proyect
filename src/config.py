# Configuration for your AI News Agent
from datetime import datetime
from zoneinfo import ZoneInfo

# Timezone configuration - set this to your local timezone
# Examples: "America/New_York", "America/Los_Angeles", "Europe/London", "Asia/Tokyo"
# Use "UTC" to keep the current behavior
TIMEZONE = "UTC"  # Change this to your timezone

LANGUAGE = "en"
MAX_RESULTS = 20
TOPICS = ["money laundering", "terrorist financing", "corruption"]

# Generate filename with date in configured timezone
def get_output_file():
    """Get output filename with current date in configured timezone."""
    tz = ZoneInfo(TIMEZONE)
    today = datetime.now(tz).date()
    return f"data/news_intelligence_{today}.json"

OUTPUT_FILE = get_output_file()
RSS_FEEDS = [
    # --- International Organizations (AML/TF/Corruption) ---
    "https://www.fatf-gafi.org/en/rss.xml",
    "https://www.transparency.org/en/rss",
    "https://www.occrp.org/en/rss",
    "https://www.europol.europa.eu/media-press/newsroom/rss.xml",
    "https://www.interpol.int/en/News-and-Events/News/rss",
    "https://news.un.org/feed/subscribe/en/news/all/rss.xml",
    "https://www.worldbank.org/en/news/all?format=rss",
    "https://www.imf.org/en/News/Articles?format=rss",

    # --- U.S. Law Enforcement ---
    "https://www.fbi.gov/news/stories/RSS",              # FBI stories & investigations
    "https://www.fbi.gov/news/press-releases/RSS",       # FBI press releases
    "https://www.fbi.gov/news/RSS",                      # FBI general news

    # --- Investigative Journalism ---
    "https://www.icij.org/feed/",                        # ICIJ (Panama Papers, financial crimes)
    "https://insightcrime.org/feed",                     # InSight Crime (organized crime, Latin America)
    "https://fcpablog.com/feed/",                        # FCPA Blog (corruption)

    # --- Major News Agencies ---
    "https://feeds.reuters.com/reuters/crimeNews",
    "https://feeds.reuters.com/Reuters/worldNews",
    "https://feeds.reuters.com/reuters/businessNews",
    "https://www.theguardian.com/world/financial-crime/rss",
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.feedburner.com/AssociatedPress/WorldNews",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://rss.dw.com/rdf/rss-en-top",

    # --- Google News Targeted Searches ---
    "https://news.google.com/rss/",
    "https://news.google.com/rss/search?q=corruption&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=anti+money+laundering&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=terrorist+financing&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=kidnapping&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=organized+crime&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=drug+trafficking&hl=en-US&gl=US&ceid=US:en",
    "https://news.google.com/rss/search?q=financial+fraud&hl=en-US&gl=US&ceid=US:en",

    # --- Multilingual News Feeds ---
    "https://news.google.com/rss?hl=es&gl=ES&ceid=ES:es",  # Spanish
    "https://news.google.com/rss?hl=it&gl=IT&ceid=IT:it",  # Italian
]
