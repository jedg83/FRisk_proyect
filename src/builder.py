import json
import os
from src import config

def save_json(new_data):
    """Save or update the structured JSON dataset."""

    # Load existing data
    if os.path.exists(config.OUTPUT_FILE):
        with open(config.OUTPUT_FILE, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []
    else:
        existing_data = []

    # Merge existing and new
    combined_data = existing_data + new_data

    # Remove duplicates (based on title + source)
    unique_data = []
    seen = set()
    for item in combined_data:
        key = (item.get("title"), item.get("source"))
        if key not in seen:
            seen.add(key)
            unique_data.append(item)

    # Save final dataset
    with open(config.OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(unique_data, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(new_data)} new records added — total {len(unique_data)} saved.")
