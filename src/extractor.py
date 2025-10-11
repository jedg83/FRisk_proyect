import spacy
from datetime import datetime

nlp = spacy.load("en_core_web_sm")

def extract_info(article):
    # Combine title + description for NER
    text = (article.get("title") or "") + " " + (article.get("description") or "")
    doc = nlp(text)

    # Named Entities
    names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    orgs = [ent.text for ent in doc.ents if ent.label_ == "ORG"]
    countries = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]
    amounts = [ent.text for ent in doc.ents if ent.label_ == "MONEY"]

    # Build structured record
    record = {
        "title": article.get("title"),
        "url": article.get("url"),
        "source": article.get("publisher", {}).get("title") if article.get("publisher") else None,
        "published_date": article.get("published date") or article.get("published_date"),
        "language": "en",
        "person_name": names[0] if names else None,
        "nationality": None,  # Placeholder: could be inferred with LLM or country lookup
        "occupation_or_role": None,  # Could be added later with LLM or regex
        "organization": orgs[0] if orgs else None,
        "country": countries[0] if countries else None,
        "city": None,  # Could add NER for cities if needed
        "crime_type": article.get("topic"),  # Based on search topic
        "crime_description": article.get("description"),
        "investigating_authority": None,
        "status": None,
        "amount_involved": amounts[0] if amounts else None,
        "risk_category": None,  # Could be inferred later
        "sector": None,
        "summary": article.get("description"),
        "sentiment": None,
        "extraction_timestamp": datetime.utcnow().isoformat(),
        "feed_url": article.get("feed_url")
    }

    return record
