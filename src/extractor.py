import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore


_openai_client: Optional["OpenAI"] = None
_openai_client_unavailable = False


def build_record(article, names=None, orgs=None, countries=None, amounts=None):
    """
    Build a structured record from a parsed article,
    with robust fallbacks and consistent key names.

    Note: AI enrichment is now done separately via batch_enrich_records()
    for better cost efficiency.
    """
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
        "person_names": article.get("people") or names,
        "organizations": article.get("organizations") or orgs,
        "locations": article.get("locations") or countries,
        # 💬 Additional Metadata
        "summary": article.get("summary") or article.get("description"),
        "sentiment": None,  # Future LLM/NLP addition
        "extraction_timestamp": datetime.utcnow().isoformat(),
        "feed_url": article.get("feed_url"),

        # Store original article for potential batch enrichment
        "_original_article": article,
    }

    return record


# --- Optional helper inference functions (simple examples) ---


def get_openai_client() -> Optional["OpenAI"]:
    """Return a cached OpenAI client if the SDK and API key are available."""

    global _openai_client, _openai_client_unavailable

    if _openai_client_unavailable:
        return None

    if _openai_client:
        return _openai_client

    if OpenAI is None:
        _openai_client_unavailable = True
        return None

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        _openai_client_unavailable = True
        return None

    try:
        _openai_client = OpenAI(api_key=api_key)
    except Exception as exc:  # pragma: no cover - network credentials issue
        print(f"⚠️ Unable to initialize OpenAI client: {exc}")
        _openai_client_unavailable = True
        return None

    return _openai_client

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

def enrich_with_ai(client, text: str) -> Optional[Dict[str, Any]]:
    """Call OpenAI to enrich the article content with structured attributes."""

    if not text:
        return None

    system_prompt = (
        "You are a compliance analyst who extracts anti-money-laundering "
        "intelligence. Always reply with valid JSON."
    )

    user_prompt = (
        "Extract structured information about AML, terrorism financing, or corruption cases "
        "mentioned in the text below. Return a JSON object with the fields: "
        "person_name, nationality, organization, crime_type, case_description, "
        "date_of_criminal_action. Use null for unknown values. Text:\n" + text
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    content = _response_to_text(response)
    if not content:
        return None

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        print("⚠️ OpenAI returned non-JSON content, skipping enrichment.")
        return None

    if isinstance(parsed, dict):
        return parsed

    return None


def _response_to_text(response: Any) -> str:
    """Support both Responses API and legacy Chat Completions payloads."""

    if hasattr(response, "output_text") and response.output_text:
        return response.output_text

    if hasattr(response, "output"):
        try:
            parts = []
            for item in response.output:  # type: ignore[attr-defined]
                for content in getattr(item, "content", []):
                    text = getattr(content, "text", "")
                    if text:
                        parts.append(text)
            if parts:
                return "".join(parts)
        except Exception:
            pass

    if hasattr(response, "choices"):
        choices = getattr(response, "choices", [])
        if choices:
            choice = choices[0]
            message = getattr(choice, "message", None)
            if message and hasattr(message, "content"):
                return message.content
            return getattr(choice, "text", "")

    return ""


# --- Batch enrichment functions (Option 1 + Option 3 combined) ---


def needs_enrichment(record: Dict[str, Any]) -> bool:
    """
    Check if a record is missing critical fields and would benefit from AI enrichment.

    Returns True if any of these critical fields are missing:
    - person_name
    - crime_type
    - organization
    """
    critical_fields = [
        "person_name",
        "crime_type",
        "organization",
    ]

    for field in critical_fields:
        if not record.get(field):
            return True

    return False


def batch_enrich_records(records: list[Dict[str, Any]], batch_size: int = 10) -> None:
    """
    Enrich multiple records with AI in batches for cost efficiency.

    This function:
    1. Filters records that need enrichment (missing critical fields)
    2. Processes them in batches to minimize API calls
    3. Updates records in-place with enriched data
    4. Only fills in missing fields, doesn't overwrite existing data

    Args:
        records: List of record dictionaries to potentially enrich
        batch_size: Number of articles to process per API call (default: 10)
    """
    client = get_openai_client()

    # Always clean up temporary article data at the end
    try:
        if not client:
            print("⚠️ OpenAI client not available, skipping AI enrichment.")
            return

        # Filter records that need enrichment
        records_needing_enrichment = [
            (i, record) for i, record in enumerate(records)
            if needs_enrichment(record)
        ]

        if not records_needing_enrichment:
            print("✅ All records have complete data, skipping AI enrichment.")
            return

        print(f"🤖 AI enrichment needed for {len(records_needing_enrichment)} out of {len(records)} records.")

        # Process in batches
        total_enriched = 0
        for batch_start in range(0, len(records_needing_enrichment), batch_size):
            batch = records_needing_enrichment[batch_start:batch_start + batch_size]

            try:
                # Prepare batch prompt
                batch_data = []
                for idx, (original_idx, record) in enumerate(batch):
                    article = record.get("_original_article", {})
                    combined_text = "\n".join(
                        filter(None, [
                            article.get("summary", ""),
                            article.get("description", "")
                        ])
                    ).strip()

                    if combined_text:
                        batch_data.append({
                            "index": idx,
                            "text": combined_text[:1000]  # Limit text length to control costs
                        })

                if not batch_data:
                    continue

                # Call OpenAI with batch
                enriched_results = _enrich_batch_with_ai(client, batch_data)

                if enriched_results:
                    # Apply results back to records
                    for idx, enriched_data in enriched_results.items():
                        if idx < len(batch):
                            original_idx, record = batch[idx]

                            # Only fill in missing fields
                            for key, value in enriched_data.items():
                                if value and not record.get(key):
                                    record[key] = value

                            total_enriched += 1

            except Exception as e:
                message = str(e)
                if "insufficient_quota" in message:
                    print("⚠️ OpenAI quota exceeded, stopping enrichment.")
                    break
                else:
                    print(f"⚠️ Batch enrichment failed: {message}")

        print(f"✅ Successfully enriched {total_enriched} records with AI.")

    finally:
        # Always clean up temporary article data
        for record in records:
            record.pop("_original_article", None)


def _enrich_batch_with_ai(client, batch_data: list[Dict[str, Any]]) -> Optional[Dict[int, Dict[str, Any]]]:
    """
    Call OpenAI to enrich multiple articles in a single API call.

    Args:
        client: OpenAI client instance
        batch_data: List of dicts with 'index' and 'text' keys

    Returns:
        Dictionary mapping index to enriched data, or None if failed
    """
    if not batch_data:
        return None

    # Build batch prompt
    system_prompt = (
        "You are a compliance analyst who extracts anti-money-laundering intelligence. "
        "Always reply with valid JSON."
    )

    # Create articles text for batch processing
    articles_text = []
    for item in batch_data:
        articles_text.append(
            f"[Article {item['index']}]\n{item['text']}\n"
        )

    combined_articles = "\n---\n".join(articles_text)

    user_prompt = (
        "Extract structured information about AML, terrorism financing, or corruption cases "
        "from the articles below. For each article, return a JSON object with these fields: "
        "person_name, nationality, organization, crime_type, case_description, date_of_criminal_action. "
        "Use null for unknown values.\n\n"
        "Return a JSON object where keys are article indices (0, 1, 2, etc.) and values are the extracted data.\n\n"
        f"Articles:\n{combined_articles}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
            max_tokens=2000,  # Control costs
        )

        content = _response_to_text(response)
        if not content:
            return None

        parsed = json.loads(content)
        if not isinstance(parsed, dict):
            return None

        # Convert string keys to integers if needed
        result = {}
        for key, value in parsed.items():
            try:
                idx = int(key)
                if isinstance(value, dict):
                    result[idx] = value
            except (ValueError, TypeError):
                continue

        return result if result else None

    except json.JSONDecodeError:
        print("⚠️ OpenAI returned non-JSON content in batch enrichment.")
        return None
    except Exception as e:
        raise e
