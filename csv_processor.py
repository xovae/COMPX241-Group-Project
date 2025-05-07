import csv
import re
import json

#Open file
with open('Warnings_and_Alerts_FMA_all.csv', encoding='utf-8-sig') as fileObject:
    
    #Create reader object
    reader = csv.reader(fileObject)
    
    #Skip the headings row
    next(reader)
    
    #Construct array to contain json entries to be written to an output file
    json_entries = []
    
    for row in reader:
        name = row[0]
        date = row[1]
        content = row[2]
        
        #Get start of description
        description_start = content.find("FSPR:")
        
        #If start is found
        if description_start != -1:
            
            #Attempt to find first common end of the description
            description_end = content.find("Entity")
            
            #If it isn't present, attempt to find the other most common end of the description
            if description_end == -1:
                description_end = content.find("Websites")
            
            #If neither strings are found, find the first occurrence of a website to mark an endpoint of the description
            if description_end == -1:
                first_match = re.search(r'\b(?:[@a-zA-Z0-9-]+\.(?=[^.]))+[a-zA-Z]{2,}\b', content)
                if first_match != None:
                    description_end = first_match.span()[0]
                else: 
                    description_end = -1
            
            #If an description end is found, capture all content between the description start and end, stripping any trailing whitespace
            if description_end != -1:
                description = content[description_start + len("FSPR:  "):description_end].rstrip()
            #Otherwise, capture everything past the description start, stripping any trailing whitespace
            else:
                description = content[description_start + len("FSPR:  "):].rstrip()
        else: 
            description = ""
            
        websites = re.findall(r'\b(?:[@a-zA-Z0-9-]+\.(?=[^.]))+[a-zA-Z]{2,}\b', content)
        # websites = re.findall(r'\b(?:[@a-zA-Z0-9-]+\.(?=[^.]))+[a-zA-Z]{2,}(?!\.)\b', content)
        websites = [valid for valid in websites if "@" not in valid]
        
        if len(websites) != 0: 
            
            #Remove duplicates
            websites = list(set(websites))
            
            #Remove trailing phrases e.g. 'Emails'
            sorted_websites = []
            
            for entry in websites:
                entry = entry[0].lower() + entry[1:]
                string = re.split(r'[A-Z]', entry)[0]
                sorted_websites.append(string)
                
            #Remove duplicates
            sorted_websites = list(set(sorted_websites))
            
            entry = {
                "Type" : "NZ",
                "Name" : name,
                "Date": date,
                "Description": description,
                "Websites": sorted_websites
            }
            
            json_entries.append(entry)
        
    with open('nz_output.json', 'w', encoding='utf-8') as file:
        json.dump(json_entries, file, indent = 2)
        
        