import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import json
import spacy
import time
from geopy.geocoders import Nominatim
import re
from collections import Counter

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)


nlp = spacy.load("en_core_web_lg")

loc = Nominatim(user_agent="GetLoc")


all_american_states = ["alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware", "florida",
          "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine",
          "maryland", "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana", "nebraska",
          "nevada", "new hampshire", "new jersey", "new mexico", "new york", "north carolina", "north dakota", "ohio",
          "oklahoma", "oregon", "pennsylvania", "rhode island", "south carolina", "south dakota", "tennessee", "texas",
          "utah", "vermont", "virginia", "washington", "west virginia", "wisconsin", "wyoming"]


def get_main_categories(url):
    page = session.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    div = soup.find("div", {"id": "mw-subcategories"})
    links = [link.get("href") for link in div.find_all("a")]
    spans = div.find_all('span', class_=lambda x: x not in {"CategoryTreeBullet", "CategoryTreeToggle", "CategoryTreeEmptyBullet"} )
    span_names = [span.text for span in spans]
    link_names = [link.text for link in div.find_all("span")]
    dic = []
    for index, aLink in enumerate(links):
        if 'C' in span_names[index]:
            final = False
        else : 
            final = True
        substring_set={"Category:Crimes", "Category:Violence"}
        if( any(substring in aLink for substring in substring_set) ):
            dic.append({"link": aLink, "span": span_names[index], "final": final})
    
    if(len(dic)==1):
        secLink = dic[0]["link"].replace("Category:Crimes", "Category:Violence")
        dic.append({"link": secLink, "span": 'C',"final": False })
    print(dic)
    return dic

def get_category_pages(url):
    excluded_cat_pages = {"September_11", "John_F._Kennedy"}
    page = session.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    div = soup.find("div", {"id": "mw-subcategories"})
    links = [link.get("href") for link in div.find_all("a")]
    links = [x for x in links]
    spans = div.find_all('span', class_=lambda x: x not in {"CategoryTreeBullet", "CategoryTreeToggle", "CategoryTreeEmptyBullet"} )
    span_names = [span.text for span in spans]
    link_names = [link.text for link in div.find_all("span")]
    dic = []
    for index, aLink in enumerate(links):
        if 'C' in span_names[index]:
            final = False
        else : 
            final = True
        if not any(p in aLink for p in excluded_cat_pages):
            dic.append({"link": aLink, "span": span_names[index], "final": final})
    
    return dic

def get_article_pages(url):
    page = session.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    parent_div = soup.find("div", {"id": "mw-pages"})
    if parent_div is not None:
        div = parent_div.find("div", class_= "mw-category")
        links = [link.get("href") for link in div.find_all("a")]
    else: 
        links=[]
    return links


def get_table_info(soup):
    detail = soup('table', {'class':'infobox'})
    date = ""
    died = ""
    location = ""
    for i in detail : 
        h= i.find_all('tr')
        for j in h: 
            heading  = j.find_all('th')
            detail = j.find_all('td')
            if heading is not None and detail is not None : 
                for x,y in zip(heading, detail):
                    if(x.text=="Date"):
                        date = y.text
                    else:
                        if(x.text=="Location"):
                            location = y.text
                        else:
                            if(x.text=="Died"):
                                died = y.text
            if died == "" and detail is not None:
                for z in detail:
                    if "Died:" in z.text:
                        died = z.text
    
    if( date == "" and died != "" ): date = died
    date = re.sub(r'\)(\S)', r') \1', date)
    return date, location

def get_paragraph(soup):
    p = ""
    for i in range(1,10):
        if(len(soup('p'))>i):
            p = p + soup('p')[i].text
    return p

def extract_year(string):
    match = re.search(r"(?<!u)(18|19|20)\d{2}", string)
    if match:
        return match.group()
    return ""

def extract_year_symentic_phrase(text):

    keywords = "raping|torture|murder|lynch|thief|looter|terror|kidnapping|riot|vandalism|kill|lynching|shoot|killing|loot|steal|dead|arrest|hijacking|kidnap|sex crime|battery|assault|hijacker|burglary|stole|rape|theft|homicide|mass murder|mass shooting|robberies|arson|kidnapp|massacre|looting|die|firearm|guilty|disappear|robber|crim|kidnapped|terrorism|shot|stab|sexual|sex abuse"

    doc = nlp(text)
    for tok in doc:
        phrase =[]
        result = []
        string = ""
        if not (tok.like_num and re.search(r"(?<!u)(18|19|20)\d{2}", tok.text) ):
            continue
        for i in tok.ancestors:
            if i.pos_ == "VERB":
                phrase.append(i)
                phrase.extend([j for j in i.children if tok in i.subtree ])
                
                for k in phrase:
                    for l in k.children:
                        if l.pos_ in {"NOUN", "VERB"}:
                            phrase.append(l)
                
                string = " ".join(f.text for f in phrase)
                if re.search(keywords, string):
                    match = re.search(keywords, string)
                    c_type = match.group()
                    c_name = crime_classifier(c_type)
                    result.append(tok.text)
                    result.append(c_name)
                    #print("new "+ c_name)
                    return result

    return ["",""]


def get_state(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "GPE" and ent.text.lower() == myState.lower():
            return ent.text
    return ""

def get_place(text):
    doc = nlp(text)
    for ent in doc.ents:
        if (ent.label_ == "GPE" and (ent.text.lower() not in all_american_states) and not (any(string in ent.text.lower() for string in {"united states", "us", "usa", "u.s.", "u.s.a" }))) :
            a = get_couty_from_geo(myState, ent.text)
            if(a != "" ):
                return ent.text
    return ""

def get_couty_from_geo(state, town):
    try:
        getLoc = loc.geocode(town+', '+state, addressdetails=True)
    except Exception:
        return ""
    if getLoc != None:
        if (getLoc.raw['address'].get("county") == None) or (getLoc.raw['address'].get("state") == None) :
            return ""
        else:
            if getLoc.raw['address'].get("state").lower() == myState.lower():
                return getLoc.raw['address']['county']
            else: 
                return ""
    else: 
        return ""


def get_crime_type(soup, title):
    found_list={}
    
    keywords = [    "killing", "murder", "homicide", "kill", "dead", "lynch", "lynching",    "shoot", "firearm", "shooting", "shot",    "mass shooting", "massacre", "mass murder",    "sex crime", "sex abuse", "sexual ", "rape", "raping",    "robber", "robberies", "robbery", "thief", "theft", "burglary", "looting", "looter", "steal", "stole", "loot",    "terrorism", "terrorist", "terror",    "kidnapping", "kidnapped", "kidnap", "disappear",    "hijacking", "hijacker",    "riot",    "arson", "vandalism",    "assault", "battery", "torture"]




    div = soup.find("div", {"id": "mw-normal-catlinks"})
    links = div.find_all("li")
    first_links = links[0:7] if len(links) >= 8 else links
    titles = [link.text for link in first_links]
    phrase = " ".join(titles)
    phrase = phrase + " " +title
    found_list = {crime_classifier(item) for item in keywords if item in phrase.lower() and crime_classifier(item) != ""}
    return found_list

def crime_classifier(word):
    word = word.lower()
    if word in {"killing", "murder", "homicide", "kill", "dead", "lynch", "lynching", "arrest", "die", "criminal", "guilty", "stab", "shot"}:
        return "murder"
    elif word in {"shoot", "firearm", "shooting"}:
        return "shooting"
    elif word in {"mass shooting", "massacre", "mass murder"}:
        return "mass murder"
    elif word in {"sex crime", "sex abuse", "sexual", "rape", "raping"}:
        return "sexual assault"
    elif word in {"robber", "robberies", "robbery", "thief", "theft", "burglary", "looting", "looter", "steal", "stole", "loot"}:
        return "robbery"
    elif word in {"terrorism", "terrorist", "terror"}:
        return "terrorism"
    elif word in {"kidnapping", "kidnapped", "kidnap", "disappear"}:
        return "kidnapping"
    elif word in {"hijacking", "hijacker"}:
        return "hijacking"
    elif word in {"riot"}:
        return "riot"
    elif word in {"arson", "vandalism"}:
        return "arson"
    elif word in {"assault", "battery", "torture"}:
        return "assault"
    else:
        return ""



states_list = [  "Texas", "California", "New York"]
for myState in states_list :
    all_links = []
    start_time = time.time()
    with open('state_cat.json', 'r') as file:
        states = json.load(file)
    for state in states:
        if state['state'] == myState:
            url = state['lien']
            file_name = state['state_name']
            break
    
    #GET MAIN CATEGORIES IN CRIME CATEGORY
    dic = get_main_categories(url)

    # EXTRACTED PAGES => [ FINAL PAGES (only articles) ] &&  [ LOOP PAGES (category pages and articles) ]
    tail_cat_pages = [element for element in dic if element["final"] == True]
    cat_pages = [element for element in dic if element["final"] == False]
    keep_going = True if len(cat_pages) > 0 else False

    #Second Round: extract all pages in subcategory pages
    keep = 0
    while(keep_going):
        keep = keep +1
        for key, element in enumerate(cat_pages): 
            new_tail_cat_pages, x, y = [], [], []
            url = "https://en.wikipedia.org"+element["link"]

            new_dic = get_category_pages(url)
            all_links.extend(get_article_pages(url))        
            
            tail = [element for element in new_dic if element["final"] == True]
            tail_cat_pages.extend(tail)
            
            cat = [element for element in new_dic if element["final"] == False]
            cat_pages.extend(cat)
            
            del cat_pages[key]
        keep_going = True if len(cat_pages) > 0 else False

    # GET ALL ARTICLES LINKS IN A FINAL PAGE 
    for element in tail_cat_pages:
        url = "https://en.wikipedia.org"+element["link"]
        links = get_article_pages(url)
        all_links.extend(links)


    # --------------------------------  EXTRACT ARTICLE INFORMATION  --------------------
    print("THE END OF LINK EXTRACTION")
    all_links = list(set(all_links))
    print(len(all_links))

    pages_data = []

    for link in all_links:
        # GET THE PAGE'S CONTENT
        url = "https://en.wikipedia.org"+link
        page = session.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        
        # (TITLE, DATE, LOCATION, PARAGRAPHS, YEAR, STATE, COUNTY AND CRIME TYPE)
        title = soup.find("h1", class_="firstHeading").text
        date, location = get_table_info(soup)
        paragraph = get_paragraph(soup) 
        
        year = extract_year(date+' '+title+' '+link)
        sem_crime = ""
        if year == "":
            year = extract_year_symentic_phrase(paragraph)[0]
            sem_crime = extract_year_symentic_phrase(paragraph)[1]        

        full_text = title + " " + location + " " + date + " " + paragraph
        the_state = get_state(full_text)
        place = get_place(full_text)
        if(the_state == ""): the_state=myState
        county = get_couty_from_geo(myState, place)
        
        crime_types = get_crime_type(soup, title + paragraph) 
        if((not len(crime_types)) and sem_crime != "" ):
            crime_types.add(sem_crime)

        
        record={"link": link, "title": title, "year": year, "state": the_state, "county": county, "type": tuple(crime_types)}   # ADD ARTICLE 
        pages_data.append(record)
        print(year, ' | ', title,' | ', county, ' | ', tuple(crime_types))
               

    last_data = {f"{i}": record for i, record in enumerate(pages_data)}     # ADD KEY TO EACH ARTICLE
    with open("state_files/"+file_name+".json", "w") as file:   # EXPORT JSON FILE
        json.dump(last_data, file, indent=4)

    overall_time = time.time() - start_time
    print(overall_time)