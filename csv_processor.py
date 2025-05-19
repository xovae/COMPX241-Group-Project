import csv
import io
import json
import re
import requests

#Download the latest copy of the CSV file
url = "https://www.fma.govt.nz/library/warnings-and-alerts/downloadWarnings/?date=all"
response = requests.get(url)
fileObject = io.StringIO(response.text)

#Download the list of valid TLDs
url = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
response = requests.get(url)
validTLDs = set(line.strip().lower() for line in response.text.splitlines() if line and not line.startswith('#'))

#Create reader object
reader = csv.reader(fileObject)

#Skip the headings row
next(reader)

#Construct array to contain json entries to be written to an output file
json_entries = []

#Stores all websites found to prevent duplicates between entries
website_cache = []

#Safe websites that are included in descriptions occasionally
whitelistedWebsites = ("netsafe.org.nz", "seek.com.au", "fca.org.uk", "nz.linkedin.com", "sorted.org.nz", "baidu.com", "co.nz", "sohu.com", "zhihu.com", "kiwibank.co.nz", "twitter.com", "youtube.com", "linkedin.com")

#Safe TLDs that are included in descriptions occasionally
whitelistedTLDs = ("govt.nz", "gov.au", "facebook.com")

#Common websites listed in scam descriptions that aren't scams

for row in reader:
    name = row[0]
    date = row[1]
    content = row[2]
    
    duplicate = False
    
    #Get start of description
    description_start = content.find("FSPR:")
    
    #If start is found
    if description_start != -1:
        
        #Attempt to find first common end of the description
        description_end = content.find("Entity")
        
        #If it isn't present, attempt to find the other most common end of the description
        if description_end == -1:
            description_end = content.find("Websites")
    
        #If an description end is found, capture all content between the description start and end, stripping any trailing whitespace
        if description_end != -1:
            description = content[description_start + len("FSPR:  "):description_end].rstrip()
        #Otherwise, capture everything past the description start, stripping any trailing whitespace
        else:
            description = content[description_start + len("FSPR:  "):].rstrip()
    else: 
        description = ""
        
    websites = re.findall(r'\b(?:[@a-zA-Z0-9-]+\.(?=[^.]))+[a-zA-Z]{2,}\b', content)
    websites = [valid for valid in websites if "@" not in valid]
    
    if len(websites) != 0: 
        
        #Remove duplicates
        websites = list(set(websites))
        
        for i in reversed(range(len(websites))):
            #Remove trailing phrases in the TLD e.g. '.comEmails'
            tldIndex = websites[i].rfind(".")
            filteredTLD = re.split(r'[A-Z]', websites[i][tldIndex:])[0]
            filteredWebsite = (websites[i][:tldIndex] + filteredTLD).lower()
            filteredWebsite = filteredWebsite.replace("www.", "")
            
            validWebsite = False
            
            #Check the website is valid (contains a valid TLD)
            while len(filteredWebsite.split('.')) > 1:
                if filteredWebsite.split('.')[1] != "":
                    if filteredWebsite.split('.')[-1] in validTLDs:
                        validWebsite = True
                        break
                    else:
                        tldIndex = filteredWebsite.rfind(".")
                        if tldIndex != -1:
                            filteredWebsite = filteredWebsite[:tldIndex]
                        else:
                            break
                else:
                    break
            
            if validWebsite == True:
                if filteredWebsite.endswith(whitelistedTLDs) == True or filteredWebsite in whitelistedWebsites:
                    del websites[i]
                else:
                    websites[i] = filteredWebsite
            else:
                del websites[i]
            
        new_websites = []
            
        for website in websites:
            #Check if the website has been listed before
            if website not in website_cache:
                website_cache.append(website)
                new_websites.append(website)
                
        # If all captured websites have been listed before, don't add the entry
        if len(new_websites) == 0:
            duplicate = True

        # If the website hasn't appeared in a previous entry, add the entry
        if duplicate == False and len(websites) != 0:
            # Remove any duplicates revealed by TLD filtering
            websites = list(set(websites))
        
            entry = {
                "Type" : "NZ",
                "Name" : name,
                "Date": date,
                "Description": description,
                "Websites": websites
            }
            
            json_entries.append(entry)
    
with open('nz_output.json', 'w', encoding='utf-8') as file:
    json.dump(json_entries, file, indent = 2)
    
        