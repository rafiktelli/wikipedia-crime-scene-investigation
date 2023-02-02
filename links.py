import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import json
import spacy
import re

session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)


nlp = spacy.load("en_core_web_md")
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
        if ent.label_ == "GPE" and ent.text.lower() in all_american_states:
            return ent.text
    return None

def get_county(text):
    doc = nlp(text)
    for ent in doc.ents:
        if (ent.label_ == "GPE" and (ent.text.lower() not in all_american_states) and not (any(string in ent.text.lower() for string in {"united states", "us", "usa", "u.s.", "u.s.a" }))) :
            return ent.text
    return None

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


all_links = []
#----------------------------------------- GET THE LINKS IN STATE CRIME CATEGORY PAGE -------------------------------------

#get the state to generate the crime articles
myState = input("State : ")
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
dic = get_category_pages(url)
a_links = get_final_page_links(url)
all_links.extend(a_links)

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
    
    paragraph = get_paragraph(soup)
    
    
    if(get_state(location)!= None):
        the_state = get_state(location)
        the_county = get_county(location)
    else:
        the_state = get_state(paragraph)
        the_county = get_county(paragraph)
    
    if(the_state == None): the_state=""
    if(the_county == None): the_county=""

    if date == "": date=died
    year = extract_year(date)
    pages_data.append({"link": link, "title": title, "date": date, "year": year, "location": location, "state": the_state, "county": the_county, "paragraph": paragraph})

#print(pages_data)

with open("states_data/"+file_name+".json", "w") as file:
    json.dump(pages_data, file, indent=4)


    