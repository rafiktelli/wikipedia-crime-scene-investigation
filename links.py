import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import json
import spacy
import time
from geopy.geocoders import Nominatim
import re

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


def get_paragraph(soup):
    p = ""
    for i in range(1,4):
        if(len(soup('p'))>i):
            p = p + soup('p')[i].text
    return p

    

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
            if(ent.text == "Marcum"): print("HHHHHHHHIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIIII")
            if(a != "" ):
                return ent.text
    return ""

def get_string(text):
    words = text.split()
    for word in words:
        if len(word) >= 4 and (word[:2] == "20" or word[:2] == "19"):
            return word[:4]
    return None

def extract_year(string):
    match = re.search(r"(?<!u)(18|19|20)\d{2}", string)
    if match:
        return match.group()
    return ""

def get_category_pages(url):
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

        dic.append({"link": aLink, "span": span_names[index], "final": final})
    
    return dic

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
    
    return dic

def get_final_page_links(url):
    page = session.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    parent_div = soup.find("div", {"id": "mw-pages"})
    if parent_div is not None:
        div = parent_div.find("div", class_= "mw-category")
        links = [link.get("href") for link in div.find_all("a")]
    else: 
        links=[]
    return links

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
    keywords=["killing", "murder", "mass murder", "rape", "riot", "arson", "assault", "homocide", "kidnapping", "kidnapped", "hijacking", "hijacker", 
            "terrorism", "terrorist", "robbery", "robber", "robberies", "torture", "battery", "lynching", "shooting", "mass shooting",
             "sex crime", "burglary", "theft", "thief", "looting", "looter" ]
    div = soup.find("div", {"id": "mw-normal-catlinks"})
    links = div.find_all("li")
    first_links = links[0:7] if len(links) >= 4 else links
    titles = [link.text for link in first_links]
    phrase = " ".join(titles)
    phrase = phrase + " " +title
    found_list = {item for item in keywords if item in phrase.lower()}
    return found_list

def extract_year_symentic_phrase(text):
    keywords = "massacre|kill|murder|shoot|shot|raping|rape|riot|kidnap|steal|stole|thief|theft|loot|robber|torture|lynch|battery|terror|arson|crim|arrest|guilty|dead|kidnapp|disappear|die"
    doc = nlp(text)
    for tok in doc:
        phrase =[]
        result = []
        string = ""
        #print(tok.text)
        if not (tok.like_num and re.search(r"(?<!u)(18|19|20)\d{2}", tok.text) ):
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
                    result.append("new "+tok.text)
                    result.append("new "+ c_name)
                    print("new "+ c_name)
                    return result

    return ["",""]

def which_crime_in_sem_year(word):
    if word in {"kill", "murder", "dead", "lynch", "crim", "arrest", "die", "guilty"}:
        return "murder"
    elif word in { "shoot", "shot", "massacre"}:
        return "shooting"
    elif word in {"raping", "rap", "sexual"}:
        return "rape"
    elif word in {"steal", "stole", "thief", "theft", "robber"}:
        return "robbery"
    elif word in {"loot"}:
        return "looting"
    elif word in {"riot"}:
        return "riots"
    elif word in {"arson"}:
        return "arson"
    elif word in {"kidnap", "disappear"}:
        return "kidnapping"
    elif word in {"torture"}:
        return "torture"
    elif word in {"terror"}:
        return "terrorism"
    elif word in {"battery"}:
        return "battery"
    else:
        return ""




all_links = []
#----------------------------------------- GET THE LINKS IN STATE CRIME CATEGORY PAGE -------------------------------------

#get the state to generate the crime articles
myState = input("State : ")
start_time = time.time()
print(start_time)
#get state category:crimes link and file_name
with open('state_cat.json', 'r') as file:
    states = json.load(file)
for state in states:
    if state['state'] == myState:
        my_url = state['lien']
        file_name = state['state_name']
        break
url = my_url
#for the main page, get all the pages that contain articles 
dic = get_main_categories(url)
#a_links = get_final_page_links(url)
#all_links.extend(a_links)

#divide the extracted pages to Final Pages (contain articles) 
#and Loop Pages (contain list of pages)
final_links_pages = [element for element in dic if element["final"] == True]
loop_pages = [element for element in dic if element["final"] == False]
keep_going = True if len(loop_pages) > 0 else False


#Second Round: extract all pages in subcategory pages
keep = 0
while(keep_going):
    keep = keep +1
    for key, element in enumerate(loop_pages): 
        new_final_links_pages, x, y = [], [], []
        url = "https://en.wikipedia.org"+element["link"]
        new_dic = get_category_pages(url)
        b_links = get_final_page_links(url)
        all_links.extend(b_links)        
        x = [element for element in new_dic if element["final"] == True]
        y = [element for element in new_dic if element["final"] == False]
        new_final_links_pages.extend(x)
        final_links_pages.extend(new_final_links_pages)
        del loop_pages[key]
        loop_pages.extend(y)
    keep_going = True if len(loop_pages) > 0 else False



#--------------------------------------- GET ALL ARTICLES IN A PAGE ---------------------
for element in final_links_pages:
    url = "https://en.wikipedia.org"+element["link"]
    links = get_final_page_links(url)
    all_links.extend(links)
# ------------------------------------------------ EXTRACT PAGE INFO --------------------
pages_data = []

for link in all_links:
    url = "https://en.wikipedia.org"+link
    #print(url)
    page = session.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    detail = soup('table', {'class':'infobox'})
    title = soup.find("h1", class_="firstHeading").text
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
    
    #When get all article info, parse the variables 
    paragraph = get_paragraph(soup) 
    sem_crime = ""
    #year extraction
    if date == "": date=died
    date = re.sub(r'\)(\S)', r') \1', date)
    year = extract_year(date+' '+title+' '+link)
    if year == "":
        year = extract_year_symentic_phrase(paragraph)[0]
        sem_crime = extract_year_symentic_phrase(paragraph)[1]
        print(year)

    #county extraction 
    full_text = title + " " + location + " " + date + " " + paragraph
    the_state = get_state(full_text)
    place = get_place(full_text)
    if(the_state == ""): the_state=myState
    g_county = get_couty_from_geo(myState, place)
    
    #crime type extraction
    crime_types = get_crime_type(soup, title + paragraph) 
    if((not len(crime_types)) and sem_crime != "" ):
        crime_types.add(sem_crime)
    else: print(crime_types)

    record={"link": link, 
            "title": title, 
            "date": date, 
            "year": year,
            "location": location, 
            "state": the_state, 
            "place": place,
            "county": g_county, 
            "paragraph": paragraph, 
            "type": tuple(crime_types)}
    
    pages_data.append(record)
    
    

#Remove duplicates
unique_records = set(tuple(record.items()) for record in pages_data)
urs = [dict(record) for record in unique_records]    
last_data = {f"{i}": record for i, record in enumerate(urs)}

#count unique records
countUnique = set(item['link'] for item in pages_data)
print(len(countUnique))

#Export the json file
with open("states_data/"+file_name+".json", "w") as file:
    json.dump(last_data, file, indent=4)

overall_time = time.time() - start_time
print(overall_time)