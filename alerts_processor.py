import csv
import io
import json
import re
import requests
    
#Stores all json entries to be written to an output file
scams_list = []

#Stores all websites found to prevent duplicates between entries
website_cache = []
    
def ASIC_processor():
    #Open file
    with open('investor-alert-list.json', encoding='utf-8-sig') as fileObject:
        
        #Create reader object
        jsonData = json.load(fileObject)

        #For every JSON file
        for entry in jsonData:
            #Protects against some None types in the JSON file
            if entry.get("websites") != None:
                #Filters out JSON entries with no websites listed
                if entry["websites"][0]:
                    if entry["dateAdded"] != None:
                        date = entry["dateAdded"]
                    else:
                        date = entry["dateUpdated"]
                    filtered_entry = {
                        "Type" : "AUS",
                        "Name" : entry["nameMandatory"],
                        "Date": date,
                        "Websites": entry["websites"]
                    }
                    
                    scams_list.append(filtered_entry)
        
def FMA_processor():
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

    #Safe websites that are included in descriptions occasionally
    whitelistedWebsites = ("netsafe.org.nz", "seek.com.au", "fca.org.uk", "nz.linkedin.com", "sorted.org.nz", "baidu.com", "co.nz", "sohu.com", "zhihu.com", "kiwibank.co.nz", "twitter.com", "youtube.com", "linkedin.com")

    #Safe TLDs that are included in descriptions occasionally
    whitelistedTLDs = ("govt.nz", "gov.au", "facebook.com")

    #Common websites listed in scam descriptions that aren't scams

    for row in reader:
        name = row[0]
        date = row[1]
        content = row[2]
        
        #Get start of description
        description_start = content.find("FSPR:")
        
        #If start is found
        if description_start != -1:
            
            #Used to filter out incorrect captures of websites in the headings
            websiteCapture = content[description_start + len("FSPR:  "): ]
            websites = re.findall(r'\b(?:[@a-zA-Z0-9-]+\.(?=[^.]))+[a-zA-Z]{2,}\b', websiteCapture)
            
            #Attempt to find first common end of the description
            description_end = content.find("Entity")
            
            #If it isn't present, attempt to find the other most common end of the description
            if description_end == -1:
                description_end = content.find("Websites")
        
            #If an description end is found, capture all content between the description start and end, stripping any trailing whitespace
            if description_end != -1:
                description = content[description_start + len("FSPR:   "):description_end].rstrip()
            #Otherwise, capture everything past the description start, stripping any trailing whitespace
            else:
                description = content[description_start + len("FSPR:   "):].rstrip()
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
                    #Remove whitelist entries
                    if filteredWebsite.endswith(whitelistedTLDs) == True or filteredWebsite in whitelistedWebsites:
                        del websites[i]
                    else:
                        #Remove echoed entries
                        length = len(filteredWebsite) - 1
                        if length % 2 == 0:
                            midpoint = len(filteredWebsite) // 2
                            if filteredWebsite[:midpoint] == filteredWebsite[midpoint+1:]:
                                websites[i] = filteredWebsite[:midpoint]
                            else:
                                websites[i] = filteredWebsite
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
                    
            #Add the entry if there are new websites listed
            if len(new_websites) != 0:

                # Remove any duplicates revealed by TLD filtering
                websites = list(set(new_websites))
                         
                entry = {
                    "Type" : "NZ",
                    "Name" : name,
                    "Date": date,
                    "Description": description,
                    "Websites": websites
                }
                
                scams_list.append(entry)
                
def IOSCO_processor():
    #Download the latest copy of the CSV file
    url = "https://www.iosco.org/i-scan/?export-to-csv&VALIDATIONDATESTART=&page=1&SUBSECTION=main&CATEGORYID=&ID=&VALIDATIONDATEEND=&PRODUCTID=&NCA_ID=&KEYWORDS="
    response = requests.get(url)
    fileObject = io.StringIO(response.text, newline ='')

    #Create reader object
    reader = csv.reader(fileObject)

    #Skip the headings row
    next(reader)
    
    no_matches = []
    
    for row in reader:
        nca = row[2]
        date = row[4]
        name = row[6]
        website = row[9]
        otherWebsites = row[10]
        domain_name = row[11]
        description = row[24]
        
        if website != "" or otherWebsites != "" or domain_name != "" and (len(websites) != 0 or len(otherWebsites) != 0 or len(domain_name) != 0):
            
            websites = [website] + otherWebsites.split('|') + [domain_name]
            
            new_websites = []
                
            for website in websites:
                #Check if the website has been listed before
                if website not in website_cache and website != "":
                    
                    #Remove trailing info
                    filteredWebsite = website.replace("www.", "")
                    filteredWebsite = filteredWebsite.replace("http://", "")
                    filteredWebsite = filteredWebsite.replace("https://", "")
                    
                    match = re.search(r'\b(?:[@a-zA-Z0-9-]+\.(?=[^.]))+[a-zA-Z]{2,}\b', filteredWebsite)
                    
                    if match != None:                
                        filteredWebsite = match.group()
                        
                        website_cache.append(filteredWebsite)
                        new_websites.append(filteredWebsite)
                    
            #Add the entry if there are new websites listed
            if len(new_websites) != 0:

                # Remove any duplicates
                websites = list(set(new_websites))
                            
                entry = {
                    "Type" : "IOSCO",
                    "NCA" : nca,
                    "Name" : name,
                    "Date": date,
                    "Description": description,
                    "Websites": websites
                }
                
                
                scams_list.append(entry)

if __name__ == '__main__':
    
    print("Processing ASIC!")
    ASIC_processor()
    
    print("Processing FMA!")
    FMA_processor()
    
    print("Processing IOSCO!")
    IOSCO_processor()
           
    with open('scams_list.json', 'w', encoding='utf-8') as file:
            json.dump(scams_list, file, indent = 2)
    