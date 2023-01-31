import os

# A string containing multiple links, separated by newlines
links_string = "https://en.wikipedia.org/wiki/Category:Crimes_in_South_Dakota\nhttps://en.wikipedia.org/wiki/Category:Crimes_in_Tennessee\nhttps://en.wikipedia.org/wiki/Category:Crimes_in_Texas\nhttps://en.wikipedia.org/wiki/Category:Crimes_in_Utah\nhttps://en.wikipedia.org/wiki/Category:Crimes_in_Vermont\nhttps://en.wikipedia.org/wiki/Category:Crimes_in_Virginia\nhttps://en.wikipedia.org/wiki/Category:Crimes_in_Washington\nhttps://en.wikipedia.org/wiki/Category:Crimes_in_West_Virginia\nhttps://en.wikipedia.org/wiki/Category:Crimes_in_Wisconsin\nhttps://en.wikipedia.org/wiki/Category:Crimes_in_Wyoming"
# Split the string into separate links
links = links_string.split("\n")

# Open each link in the default web browser
for link in links:
    os.system(f"start {link}")