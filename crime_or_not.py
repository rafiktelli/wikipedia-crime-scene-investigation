import spacy 
import re
nlp = spacy.load("en_core_web_md")



def which_crime_in_sem_year(word):
    if word in {"kill", "murder", "dead", "lynch"}:
        return "murder"
    elif word in { "shoot", "shot", "massacre"}:
        return "shooting"
    elif word in {"raping", "rap", "sexual"}:
        return "rape"
    elif word in {"steal", "stole", "thief", "theft", "robber"}:
        return "robbery"
    elif word in {"loot"}:
        return "looting"
    elif word in {"arson"}:
        return "arson"
    elif word in {"kidnap"}:
        return "kidnapping"
    elif word in {"torture"}:
        return "torture"
    elif word in {"terror"}:
        return "terrorism"
    elif word in {"battery"}:
        return "battery"
    else:
        return ""





def extract_year_symentic_phrase(text):
    keywords = "massacre|kill|murder|shoot|shot|raping|rape|sexual|riot|kidnap|steal|stole|thieft|theft|loot|robber|torture|lynch|battery|terror|arson|crim|arrest|guilty|dead"
    doc = nlp(text)
    for tok in doc:
        phrase =[]
        result =[]
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
                    match = re.search(keywords, string)
                    c_type = match.group()
                    c_name = which_crime_in_sem_year(c_type)
                    result.append(tok.text)
                    result.append(c_name)
                    return result[1]

    return ""

#doc = nlp('On 1965, two people found dead. DC is the twenty second episode of the third season of the television show Buffy the Vampire Slayer. It was written by Jane Espenson, directed by Regis Kimble, and first broadcast, out of sequence, on September 21, 1999. The originally scheduled broadcast was postponed following the Columbine High School massacre on April 20, 1999.')

doc = "In 2014, the offenser killed four ladies before he went to sleep "


x = extract_year_symentic_phrase(doc)
print(x)

























#array = []
#for ent in doc.ents:
#    if ent.label_ != "DATE":
#        continue
#    if re.search("massacre|kill|murder|shoot", ent.sent.text):
#        array.append(ent.text)

#print(array)