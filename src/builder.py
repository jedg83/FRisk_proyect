import json
from src import config

def save_json(data):
    with open(config.OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ JSON saved at {config.OUTPUT_FILE}")
