import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from src.collector import collect_news
from src.extractor import build_record, batch_enrich_records
from src.builder import save_json
from src import config


def main(output_date=None):
    """
    Main function to collect, extract, and save news data.

    Args:
        output_date: Optional date string (YYYY-MM-DD) to override the output filename date
    """
    # Override OUTPUT_FILE if custom date provided
    if output_date:
        config.OUTPUT_FILE = f"data/news_intelligence_{output_date}.json"
        print(f"📅 Using custom date for output: {output_date}")
    else:
        # Show which timezone is being used
        tz_name = config.TIMEZONE
        tz = ZoneInfo(tz_name)
        current_date = datetime.now(tz).date()
        print(f"📅 Using {tz_name} timezone. Current date: {current_date}")

    print("📰 Collecting news...")
    articles = collect_news()
    print(f"Found {len(articles)} articles.")

    print("🔍 Extracting information...")
    structured = [build_record(a) for a in articles]

    # AI Enrichment (batch processing for cost efficiency)
    print("🤖 Checking for records needing AI enrichment...")
    batch_enrich_records(structured, batch_size=10)

    print("💾 Saving JSON file...")
    save_json(structured)
    print(f"✅ Data saved to: {config.OUTPUT_FILE}")
    return structured


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="AI News Intelligence Agent - Collect and analyze AML/TF/Corruption news"
    )
    parser.add_argument(
        "--date",
        type=str,
        help="Override output date (format: YYYY-MM-DD). If not specified, uses current date in configured timezone."
    )
    parser.add_argument(
        "--timezone",
        type=str,
        help="Override timezone setting (e.g., 'America/New_York', 'Europe/London')"
    )

    args = parser.parse_args()

    # Override timezone if provided
    if args.timezone:
        try:
            # Validate timezone
            ZoneInfo(args.timezone)
            config.TIMEZONE = args.timezone
            # Regenerate OUTPUT_FILE with new timezone
            config.OUTPUT_FILE = config.get_output_file()
            print(f"🌍 Timezone overridden to: {args.timezone}")
        except Exception as e:
            print(f"❌ Invalid timezone '{args.timezone}': {e}")
            exit(1)

    main(output_date=args.date)
