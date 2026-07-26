# FRisk_proyect

Data Engineer to automate with AI agents evalutations of the alerts. This include an AI-powered agent that collects and analyzes global news related to money laundering, terrorist financing, and corruption, and outputs structured JSON data.

## AI News Intelligence Agent

This project is an **AI-powered agent** that automatically collects and analyzes global news related to **money laundering**, **terrorist financing**, and **corruption**.

It extracts key entities (people, countries, crimes, and dates) and stores the information in a structured **JSON** format.

---

## Features

- Collects news from multiple sources using `gnews`
- Uses **spaCy** for entity extraction (names, locations, dates)
- Generates structured JSON datasets
- Simple modular design, ready for automation

---

## Installation

```bash
git clone https://github.com/<your-username>/ai-news-intelligence-agent.git
cd ai-news-intelligence-agent
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm

---

## Execution

### Basic Usage
```bash
cd /workspaces/FRisk_proyect && python3 -m pip install -r requirements.txt && python3 -m src.main
```

### Timezone Configuration

**Important:** By default, the project uses UTC timezone for file naming. If you're running this in a Codespace or cloud environment at 11pm in your local timezone, the file might be created with the next day's date because the system time is in UTC.

**To fix this, you have two options:**

1. **Configure your timezone in config.py:**
   Edit `src/config.py` and change the `TIMEZONE` setting:
   ```python
   TIMEZONE = "America/New_York"  # or your timezone
   ```

   Common timezones:
   - `America/New_York` (EST/EDT)
   - `America/Los_Angeles` (PST/PDT)
   - `Europe/London` (GMT/BST)
   - `Asia/Tokyo` (JST)
   - `UTC` (default)

2. **Use command-line arguments:**
   ```bash
   # Override timezone for this run
   python3 -m src.main --timezone "America/New_York"

   # Override output date manually
   python3 -m src.main --date "2026-07-23"

   # Combine both
   python3 -m src.main --timezone "America/Los_Angeles" --date "2026-07-22"
   ```

### Command-Line Options
- `--timezone TIMEZONE`: Override the timezone setting (e.g., 'America/New_York')
- `--date YYYY-MM-DD`: Override the output file date manually

### Output Files
The script creates files in the format: `data/news_intelligence_{date}.json`
- The date is determined by the current date in your configured timezone
- Files are automatically deduplicated and merged with existing data

