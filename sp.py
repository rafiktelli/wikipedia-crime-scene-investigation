import spacy

nlp = spacy.load("en_core_web_sm")

states = ["alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware", "florida",
          "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine",
          "maryland", "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana", "nebraska",
          "nevada", "new hampshire", "new jersey", "new mexico", "new york", "north carolina", "north dakota", "ohio",
          "oklahoma", "oregon", "pennsylvania", "rhode island", "south carolina", "south dakota", "tennessee", "texas",
          "utah", "vermont", "virginia", "washington", "west virginia", "wisconsin", "wyoming"]

def get_state(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "GPE" and ent.text.lower() in states:
            return ent.text
    return None

text = "I live in New mexico and New York"
state = get_state(text)
print("State:", state)