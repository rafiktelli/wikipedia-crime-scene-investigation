import spacy 
import re
nlp = spacy.load("en_core_web_md")

def extract_year_symentic_phrase(text):
    keywords = "massacre|kill|murder|shoot|shot|raping|rape|riot|kidnap|steal|stole|thieft|theft|loot|robber|torture|lynch|battery|terror|arson|crim|arrest|guilty|dead|kidnapp"
    doc = nlp(text)
    for tok in doc:
        phrase =[]
        string = ""
        #print(tok.text)
        if not (tok.like_num and re.search(r"(?<!u)(17|18|19|20)\d{2}", tok.text) ):
            continue
        for i in tok.ancestors:
            if i.pos_ == "VERB":
                phrase.append(i)
                phrase.extend([j for j in i.children if j.dep_ == "dobj" and tok in i.subtree ])
                
                for k in phrase:
                    for l in k.children:
                        if l.pos_ in {"NOUN", "VERB"}:
                            phrase.append(l)
                
                string = " ".join(f.text for f in phrase)
                print(string)
                if re.search(keywords, string):
                    return tok.text

    return ""

#doc = nlp('On 1965, two people found dead. DC is the twenty second episode of the third season of the television show Buffy the Vampire Slayer. It was written by Jane Espenson, directed by Regis Kimble, and first broadcast, out of sequence, on September 21, 1999. The originally scheduled broadcast was postponed following the Columbine High School massacre on April 20, 1999.')

doc = " In the state of Hawaii, the common law felony murder rule has been completely abolished.[1]\nIn Hawaii Revised Statutes \u00a7707-701, the Hawaii State Legislature noted the critical history of the felony murder rule and the severe limitation of it in the Model Penal Code.  The legislature determined that the commission of a felony should not serve to automatically classify an offense as murder, and that a separate factual inquiry should be undertaken for each case to determine the significance of a felony on the severity of the offense. "


x = extract_year_symentic_phrase(doc)
print(x)

























#array = []
#for ent in doc.ents:
#    if ent.label_ != "DATE":
#        continue
#    if re.search("massacre|kill|murder|shoot", ent.sent.text):
#        array.append(ent.text)

#print(array)