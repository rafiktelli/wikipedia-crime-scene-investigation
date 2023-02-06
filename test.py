keywords = "raping|torture|murder|lynch|thief|looter|terror|kidnapping|riot|vandalism|kill|lynching|shoot|killing|loot|steal|dead|arrest|hijacking|kidnap|sex crime|battery|assault|hijacker|burglary|stole|rape|theft|homicide|mass murder|mass shooting|robberies|arson|kidnapp|massacre|looting|die|firearm|gun|guilty|disappear|robber|crim|kidnapped|terrorism"


keywords = "massacre|kill|murder|shoot|shot|raping|rape|riot|kidnap|steal|stole|thief|floot|robber|torture|lynch|battery|terror|arson|crim|arrest|guilty|dead|kidnapp|disappear|die"


xmd = [  "Alabama", "Alaska", "Arizona", "Arkansas", "Colorado", "Connecticut",  "Delaware",    "Kansas",    "Kentucky",    "Louisiana",    "Maine",    "Maryland",    "Massachusetts",    "Michigan",    "Minnesota",    "Mississippi",    "Missouri",    "Montana",    "Nebraska",    "Nevada",    "New Hampshire", "Delaware", "New Jersey", "New Mexico", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming", "California"]


record={"link": link, "title": title, "date": date, "year": year, "location": location, "state": the_state, "place": place, "county": county, "paragraph": paragraph, "type": tuple(crime_types)}


#Remove duplicates

    #unique_records = set(tuple(record.items()) for record in pages_data)
    #urs = [dict(record) for record in unique_records]    
    print("total number of articles:")
    print(len(pages_data))
    #print("number of unique articles: ")
    #print(len(last_data))
    