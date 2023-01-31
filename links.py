import requests
from bs4 import BeautifulSoup
import json
import spacy

nlp = spacy.load("en_core_web_sm")
all_american_states = ["alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware", "florida",
          "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine",
          "maryland", "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana", "nebraska",
          "nevada", "new hampshire", "new jersey", "new mexico", "new york", "north carolina", "north dakota", "ohio",
          "oklahoma", "oregon", "pennsylvania", "rhode island", "south carolina", "south dakota", "tennessee", "texas",
          "utah", "vermont", "virginia", "washington", "west virginia", "wisconsin", "wyoming"]


#--------------------------------------------------------------------------------------
def get_state(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "GPE" and ent.text.lower() in all_american_states:
            return ent.text
    return None

#--------------------------------------------------------------------------------------
def get_county(text):
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "GPE" and ent.text.lower() not in all_american_states and not (any(string in ent.text.lower() for string in {"united states", "us", "usa", "u.s.", "u.s.a" })) :
            return ent.text
    return None


#--------------------------------------------------------------------------------------
def get_string(text):
    words = text.split()
    for word in words:
        if len(word) >= 4 and (word[:2] == "20" or word[:2] == "19"):
            return word[:4]
    return None
#--------------------------------------------------------------------------------------


input_val = input("State : ")

with open('state_cat.json', 'r') as file:
    states = json.load(file)

for state in states:
    if state['state'] == input_val:
        my_url = state['lien']
        file_name = state['state_name']
        print("le lien est : "+my_url)
        break


url = my_url
page = requests.get(url)
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
#print(dic)
final_links_pages = [element for element in dic if element["final"] == True]
loop_pages = [element for element in dic if element["final"] == False]

#print(loop_pages)

keep_going = True if len(loop_pages) > 0 else False



#Second Round 
cpt = 0
keep = 0
while(keep_going):
    #print("keep going : ")
    keep = keep +1
    #print(keep)
    for key, element in enumerate(loop_pages): 
        new_final_links_pages = []
        x=[]
        y=[]
        cpt=cpt +1
        #print(cpt)
        url = "https://en.wikipedia.org"+element["link"]
        #print("this is the url : "+ url)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        div = soup.find("div", {"id": "mw-subcategories"})
        links = [link.get("href") for link in div.find_all("a")]
        spans = div.find_all('span', class_=lambda x: x not in {"CategoryTreeBullet", "CategoryTreeToggle", "CategoryTreeEmptyBullet"} )
        span_names = [span.text for span in spans]
        link_names = [link.text for link in div.find_all("span")]
        new_dic = []
        for index, aLink in enumerate(links):
            if 'C' in span_names[index]:
                final = False
            else : 
                final = True
            new_dic.append({"link": aLink, "span": span_names[index], "final": final})
        #print(new_dic)
        
        x = [element for element in new_dic if element["final"] == True]
        y = [element for element in new_dic if element["final"] == False]
        new_final_links_pages.extend(x)
        final_links_pages.extend(new_final_links_pages)
        #final_links_pages.extend(new_final_links_pages)
        del loop_pages[key]
        loop_pages.extend(y)
    keep_going = True if len(loop_pages) > 0 else False
    #print("loop_pages length: ")
    #print(len(loop_pages))
    #print("final_links_pages length: ")
    #print(len(final_links_pages))

#print(final_links_pages)


#------------------------------------------------- JUST TRYING ------------------------------------
all_links = []
for element in final_links_pages:
    url = "https://en.wikipedia.org"+element["link"]
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    div = soup.find("div", class_= "mw-category")

    links = [link.get("href") for link in div.find_all("a")]
    #print("these are the links: ")
    #print(links)
    all_links.extend(links)

#print(all_links)

# ------------------------------------------------ JUST TRYING EXTRACT PAGE INFO --------------------

pages_data = []

for link in all_links:
    url = "https://en.wikipedia.org"+link
    #print(url)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    detail = soup('table', {'class':'infobox'})
    title = soup.find("h1", class_="firstHeading").text
    date = ""
    location = ""
    paragraph = ""
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
    for i in range(1,3):
        if(len(soup('p'))>i):
            paragraph = paragraph + soup('p')[i].text
    
    if(get_state(location)!= None):
        the_state = get_state(location)
        the_county = get_county(location)
    else:
        the_state = get_state(paragraph)
        the_county = get_county(paragraph)
    
    if(the_state == None): the_state=""
    if(the_county == None): the_county=""

    pages_data.append({"link": link, "title": title, "date": date, "location": location, "state": the_state, "county": the_county, "paragraph": paragraph})

#print(pages_data)

with open("states_data/"+file_name+".json", "w") as file:
    json.dump(pages_data, file, indent=4)


    