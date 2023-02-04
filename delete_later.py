from geopy.geocoders import Nominatim
loc = Nominatim(user_agent="GetLoc")
 
# entering the location name
town = "the City of Chicago's"
state = "Illinois"
getLoc = loc.geocode(town+', '+state, addressdetails=True)
#print(getLoc.raw['address'])
if getLoc != None:
    if getLoc.raw['address'].get("county") == None:
        print("not found")
    else:
        print(getLoc.raw['address']['county'])
        print(getLoc.raw['address'])
    