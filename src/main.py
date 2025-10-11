from src.collector import collect_news
from src.extractor import extract_info
from src.builder import save_json

def main():
    print("📰 Collecting news...")
    articles = collect_news()
    print(f"Found {len(articles)} articles.")

    print("🔍 Extracting information...")
    structured = [extract_info(a) for a in articles]

    print("💾 Saving JSON file...")
    save_json(structured)

if __name__ == "__main__":
    main()
