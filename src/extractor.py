import spacy

nlp = spacy.load("en_core_web_sm")

def extract_info(article):
    doc = nlp(article["title"] + " " + article["description"])
    names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
    countries = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    dates = [ent.text for ent in doc.ents if ent.label_ == "DATE"]

    return {
        "person_name": names[0] if names else None,
        "country": countries[0] if countries else None,
        "nationality": None,
        "case_description": article["description"],
        "crime_description": article["topic"],
        "date_of_action": dates[0] if dates else None,
        "source": article["publisher"]["title"]
    }
