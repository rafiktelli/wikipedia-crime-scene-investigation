import requests
from bs4 import BeautifulSoup

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
    return date, location


url = "https://en.wikipedia.org/wiki/2014_Isla_Vista_killings"
page = requests.get(url)
soup = BeautifulSoup(page.content, "html.parser")
date, location = get_table_info(soup)

print(date)
print(location)
        