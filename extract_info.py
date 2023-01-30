import requests
import string
from bs4 import BeautifulSoup

Enter_input = input("Search: ")
u_i = string.capwords(Enter_input)
lists= u_i.split()
word = "_".join(lists)

url = "https://en.wikipedia.org/wiki/"+word

def wikibot(url):
    url_open = requests.get(url)
    #print(url_open.status_code)
    if(url_open.status_code != 404):
        soup = BeautifulSoup(url_open.content,'html.parser')
        detail = soup('table', {'class':'infobox'})
        title = soup.find("h1", class_="firstHeading").text
        paragraph = ""
        date = ""
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
        for i in range(1,4):
            paragraph = paragraph + soup('p')[i].text
        print(title)
        print(date)
        print(location)
        #print(paragraph)
    else:
        print("this page is unfound")
    
wikibot(url)