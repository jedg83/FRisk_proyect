import os
import json
from openai import OpenAI
from datetime import datetime




def build_record(article, names=None, orgs=None, countries=None, amounts=None):
    """
    Build a structured record from a parsed article, 
    with robust fallbacks and consistent key names.
    """
    # client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    names = names or []
    orgs = orgs or []
    countries = countries or []
    amounts = amounts or []

    record = {
        # 📰 Basic Metadata
        "title": article.get("title") or article.get("headline"),
        "url": article.get("link") or article.get("url"),
        "source": (
            article.get("publisher", {}).get("title")
            if isinstance(article.get("publisher"), dict)
            else article.get("source") or article.get("feed_url")
        ),
        "published_date": (
            article.get("published_date")
            or article.get("published date")
            or article.get("date")
        ),
        "language": article.get("language", "unknown"),

        # 👤 Entities and Context
        "person_name": names[0] if names else None,
        "organization": orgs[0] if orgs else None,
        "country": countries[0] if countries else None,
        "nationality": article.get("country") or countries[0] if countries else None,
        "occupation_or_role": None,  # Optional: could be extracted with regex or LLM
        "city": None,  # Optional: future NER enhancement

        # ⚖️ Crime and Case Info
        "crime_type": article.get("topic") or infer_crime_type(article),
        "crime_description": article.get("description") or article.get("summary"),
        "investigating_authority": None,
        "status": infer_case_status(article.get("description", "")),
        "amount_involved": amounts[0] if amounts else None,
        "risk_category": infer_risk_category(article),
        "sector": infer_sector(article),
        "person_names": article.get("people"),
        "organizations": article.get("orgs"),
        "locations": article.get("locations"),
        # 💬 Additional Metadata
        "summary": article.get("summary") or article.get("description"),
        "sentiment": None,  # Future LLM/NLP addition
        "extraction_timestamp": datetime.utcnow().isoformat(),
        "feed_url": article.get("feed_url"),
    }

    #if client:
    #        try:
                # Combine relevant text fields for AI enrichment
    #           combined_text = f"{article.get('summary', '')}\n{article.get('description', '')}"
                # enriched_json = None # enrich_with_ai(client, combined_text)

    #            try:
                    # Parse and merge enrichment
    #                enriched_data = json.loads(enriched_json)
    #                if isinstance(enriched_data, dict):
    #                    record["ai_enrichment"] = enriched_data  # ✅ add results as subfield
    #            except json.JSONDecodeError:
    #                print(f"⚠️ AI enrichment returned invalid JSON for article: {record['title']}")

    #        except Exception as e:
    #            if not "insufficient_quota" in str(e):
                    #print("⚠️ OpenAI quota exceeded, skipping enrichment.")
    #                print(f"⚠️ Error during AI enrichment: {e}")
                    #raise

    return record


# --- Optional helper inference functions (simple examples) ---

def infer_crime_type(article):
    text = (article.get("title", "") + " " + article.get("description", "")).lower()
    if "lavado" in text or "laundering" in text:
        return "Money Laundering"
    elif "corrup" in text:
        return "Corruption"
    elif "terror" in text:
        return "Terrorist Financing"
    elif "fraud" in text or "fraude" in text:
        return "Fraud"
    return None


def infer_case_status(text):
    text = text.lower()
    if "sentenced" in text or "condenado" in text:
        return "Sentenced"
    elif "investigation" in text or "investigación" in text:
        return "Under Investigation"
    elif "charged" in text or "acusado" in text:
        return "Charged"
    elif "arrested" in text or "detenido" in text:
        return "Arrested"
    return None


def infer_risk_category(article):
    text = (article.get("title", "") + " " + article.get("description", "")).lower()
    if any(k in text for k in ["bank", "banco", "fintech"]):
        return "Financial Sector"
    elif any(k in text for k in ["politician", "gobierno", "minister", "presidente"]):
        return "Political Exposure"
    elif any(k in text for k in ["ngo", "charity", "foundation"]):
        return "Nonprofit Risk"
    return "General"


def infer_sector(article):
    text = (article.get("title", "") + " " + article.get("description", "")).lower()
    if any(k in text for k in ["construction", "infraestructura", "obra pública"]):
        return "Construction"
    elif any(k in text for k in ["oil", "petróleo", "energía"]):
        return "Energy"
    elif any(k in text for k in ["bank", "banco", "fintech"]):
        return "Finance"
    elif any(k in text for k in ["mining", "mina", "oro"]):
        return "Mining"
    return None

def enrich_with_ai(client, text):
    prompt = f"""
    Extract structured information about AML, TF, or corruption cases from the following text.
    Respond in JSON format with fields:
    person_name, nationality, organization, crime_type, case_description, date_of_criminal_action.
    
    Text:
    {text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content