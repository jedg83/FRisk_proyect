# FRisk_proyect
Data Engineer to automate with AI agents evalutations of the alerts. This include an AI-powered agent that collects and analyzes global news related to money laundering, terrorist financing, and corruption, and outputs structured JSON data.


# AI News Intelligence Agent

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
```

---

## Testing

There is no automated test suite yet, but you can verify the project works using the following manual checks.

### 1. Run the full pipeline end-to-end
The simplest smoke test — collects real news, extracts entities, and writes the JSON output:
```bash
python -m src.main
```
Check the console output for collected/extracted counts, then confirm a file was created at `data/news_intelligence_<date>.json`.

### 2. Test the collector in isolation
Fetches and filters RSS entries without running the full pipeline:
```bash
python -c "from src.collector import collect_news; news = collect_news(); print(len(news)); print(news[0] if news else 'No matching articles found')"
```
Useful for checking whether `config.RSS_FEEDS` are reachable and whether `is_relevant_news` is filtering as expected.

### 3. Test relevance filtering and entity extraction with sample text
No network calls required — good for quick iteration on keyword/regex rules:
```bash
python -c "
from src.collector import is_relevant_news, extract_entities
print(is_relevant_news('Bank fined for money laundering violations', ''))
print(extract_entities('John Smith was arrested in Panama for bribery at Acme Corp.'))
"
```

### 4. Test record building without an OpenAI API key
`build_record` works even without `OPENAI_API_KEY` set (AI enrichment is skipped gracefully):
```bash
python -c "
from src.extractor import build_record
article = {
    'title': 'Executive charged with fraud',
    'summary': 'A bank executive was charged with fraud and money laundering.',
    'link': 'https://example.com/article',
    'source': 'Example News',
    'people': ['Jane Doe'],
    'organizations': ['Example Bank'],
    'locations': ['Panama'],
}
import json
print(json.dumps(build_record(article), indent=2))
"
```
To test AI enrichment, set `OPENAI_API_KEY` in your environment first and confirm the resulting record includes an `ai_enrichment` field.

### 5. Test JSON saving and de-duplication
Verifies `save_json` merges and de-duplicates records correctly:
```bash
python -c "
from src.builder import save_json
save_json([{'title': 'Sample', 'source': 'Test'}])
save_json([{'title': 'Sample', 'source': 'Test'}])  # duplicate, should not add a new entry
"
```
Inspect `config.OUTPUT_FILE` afterward to confirm only one record was kept.

### 6. Inspect the output JSON manually
After any run, open the generated file under `data/` and check that each record has the expected fields (`title`, `url`, `source`, `person_names`, `organizations`, `locations`, `crime_type`, etc.).
