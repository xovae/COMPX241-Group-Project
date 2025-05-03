import json

#Open file
with open('investor-alert-list.json', encoding='utf-8-sig') as fileObject:
    
    #Create reader object
    jsonData = json.load(fileObject)
    
    #Construct array to contain JSON entries to be written to an output file
    json_entries = []

    #For every JSON file
    for entry in jsonData:
        #Protects against some None types in the JSON file
        if entry.get("websites") != None:
            #Filters out JSON entries with no websites listed
            if entry["websites"][0]:
                json_entries.append(entry)
            
with open('aus_output.json', 'w', encoding='utf-8') as file:
        json.dump(json_entries, file, indent = 2)
        