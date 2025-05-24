import csv
import io
import json
import re
import requests
    
#Stores all json entries to be written to an output file
scamsList = []

#Stores all websites found to prevent duplicates between entries
websiteCache = []

#Safe websites that are included in descriptions occasionally
whitelistedWebsites = ("netsafe.org.nz", "seek.com.au", "fca.org.uk", "nz.linkedin.com", "sorted.org.nz", "baidu.com", "co.nz", "sohu.com", "zhihu.com", "kiwibank.co.nz", "twitter.com", "youtube.com", "linkedin.com", "facebook.com", "en-gb.facebook.com", "sfc.hk")

#Safe TLDs that are included in descriptions occasionally
whitelistedTLDs = ("govt.nz", "gov.au")

#Download the list of valid TLDs
url = "https://data.iana.org/TLD/tlds-alpha-by-domain.txt"
response = requests.get(url)
validTLDs = set(line.strip().lower() for line in response.text.splitlines() if line and not line.startswith('#'))

#Add TLDs not managed by IANA
validTLDs.update(["bbs", "chan", "cyb", "dyn", "geek", "gopher", "indy", "libre", "neo", "null", "o", "oss", "oz", "parody", "pirate", "fur", "lib", "coin", "emc", "bazar", "ku", "te", "ti", "uu", "ko", "rm"])
   
def ASICProcessor():
    #Open file
    with open('investor-alert-list.json', encoding='utf-8-sig') as fileObject:
        
        #Create reader object
        jsonData = json.load(fileObject)

        #For every JSON file
        for entry in jsonData:
            #Filter out empty entries or ones valued None in the JSON file
            if entry.get("websites") and entry["websites"][0]:
                
                    #Manually check the name as a backup for misinputted websites in other fields
                    matches = re.findall(r'\b(?:[@a-zA-Z0-9-]+\.(?=[^.]))+[a-zA-Z]{2,}\b', entry["nameMandatory"])
                    if matches != None:
                        nameWebsites = matches
                
                    #Filter and capture all usable websites
                    newWebsites = filterWebsites(entry["websites"] + nameWebsites)
                              
                    #Add the entry only if there are new websites listed                              
                    if len(newWebsites) != 0:
                        
                        #Get date of listing
                        if entry["dateAdded"] != None:
                            date = entry["dateAdded"]
                        else:
                            date = entry["dateUpdated"]
                            
                        #Get additional info if present
                        if entry["otherInformationGeneral"] != "":
                            description = entry["otherInformationGeneral"]
                        else:
                            description = None
                        
                        #Construct JSON entry with fields depending on if "otherInformationGeneral" had content or not
                        if description != None:
                            filteredEntry = {
                                "Type" : "AUS",
                                "Name" : entry["nameMandatory"],
                                "Date": date,
                                "Description": description,
                                "Websites": newWebsites
                            }
                        else:
                            filteredEntry = {
                                "Type" : "AUS",
                                "Name" : entry["nameMandatory"],
                                "Date": date,
                                "Websites": newWebsites
                            }
                        
                        scamsList.append(filteredEntry)

def FMAProcessor():
    #Download the latest copy of the CSV file
    url = "https://www.fma.govt.nz/library/warnings-and-alerts/downloadWarnings/?date=all"
    response = requests.get(url)
    fileObject = io.StringIO(response.text)

    #Create reader object
    reader = csv.reader(fileObject)

    #Skip the headings row
    next(reader)

    for row in reader:
        name = row[0]
        date = row[1]
        content = row[2]
        
        #Get start of description
        descriptionStart = content.find("FSPR:")
        
        #If start is found
        if descriptionStart != -1:
            
            #Used to filter out incorrect captures of websites in the headings
            websiteCapture = content[descriptionStart + len("FSPR:  "): ]
            websites = re.findall(r'\b(?:[@a-zA-Z0-9-]+\.(?=[^.]))+[a-zA-Z]{2,}\b', websiteCapture)
            
            #Attempt to find first common end of the description
            descriptionEnd = content.find("Entity")
            
            #If it isn't present, attempt to find the other most common end of the description
            if descriptionEnd == -1:
                descriptionEnd = content.find("Websites")
        
            #If an description end is found, capture all content between the description start and end, stripping any trailing whitespace
            if descriptionEnd != -1:
                description = content[descriptionStart + len("FSPR:   "):descriptionEnd].rstrip()
            #Otherwise, capture everything past the description start, stripping any trailing whitespace
            else:
                description = content[descriptionStart + len("FSPR:   "):].rstrip()
        else: 
            description = ""
            websites = re.findall(r'\b(?:[@a-zA-Z0-9-]+\.(?=[^.]))+[a-zA-Z]{2,}\b', content)
    
        websites = [valid for valid in websites if "@" not in valid]
        
        if len(websites) != 0: 
            
            #Filter and capture all usable websites
            newWebsites = filterWebsites(websites)
                            
            #Add the entry only if there are new websites listed
            if len(newWebsites) != 0:

                # Remove any duplicates revealed by TLD filtering
                newWebsites = list(set(newWebsites))
                         
                entry = {
                    "Type" : "NZ",
                    "Name" : name,
                    "Date": date,
                    "Description": description,
                    "Websites": newWebsites
                }
                
                scamsList.append(entry)
 
def IOSCOProcessor():
    #Download the latest copy of the CSV file
    url = "https://www.iosco.org/i-scan/?export-to-csv&VALIDATIONDATESTART=&page=1&SUBSECTION=main&CATEGORYID=&ID=&VALIDATIONDATEEND=&PRODUCTID=&NCA_ID=&KEYWORDS="
    response = requests.get(url)
    fileObject = io.StringIO(response.text, newline ='')
  
    #Create reader object
    reader = csv.reader(fileObject)

    #Skip the headings row
    next(reader)
    
    for row in reader:
        nca = row[2]
        date = row[4]
        name = row[6]
        url = row[5]
        website = row[9]
        otherWebsites = row[10]
        domainName = row[11]
        description = row[24]
        
        #If a website has been listed in any of the applicable fields
        if website != "" or otherWebsites != "" or domainName != "" and (len(websites) != 0 or len(otherWebsites) != 0 or len(domainName) != 0):
            
            #Manually check the description as a backup for misinputted websites in other fields
            matches = re.findall(r'\b(?:[@a-zA-Z0-9-]+\.(?=[^.]))+[a-zA-Z]{2,}\b', description)
            if matches != None:
                descriptionWebsites = matches
            
            #Combine all entries
            websites = [website] + otherWebsites.split('|') + [domainName] + descriptionWebsites
            
            #Filter and capture all usable websites
            newWebsites = filterWebsites(websites)
                    
            #Add the entry if there are new websites listed
            if len(newWebsites) != 0:
                           
                entry = {
                    "Type" : "IOSCO",
                    "NCA" : nca,
                    "URL" : url,
                    "Name" : name,
                    "Date": date,
                    "Description": description,
                    "Websites": newWebsites
                }
                
                scamsList.append(entry)

def filterWebsites(websites):
    newWebsites = []
    
    #Remove duplicates
    websites = list(set(websites))
                        
    for website in websites:
        #Remove trailing phrases in the TLD e.g. '.comEmails'
        tldIndex = website.rfind(".")
        filteredTLD = re.split(r'[A-Z]', website[tldIndex:])[0]
        filteredWebsite = (website[:tldIndex] + filteredTLD).lower()

        #Remove prefixes
        filteredWebsite = filteredWebsite.replace("www.", "")
        filteredWebsite = filteredWebsite.replace("http://", "")
        filteredWebsite = filteredWebsite.replace("https://", "")
        
        #Extract website from string
        match = re.search(r'\b(?:[@a-zA-Z0-9-]+\.(?=[^.]))+[a-zA-Z]{2,}\b', filteredWebsite)

        #If a valid website is found
        if match != None:                
            filteredWebsite = match.group()
        
            validWebsite = False
    
            #Filter websites by checking if the TLD is valid. Strips a TLD every time it's invalid until the string is no longer a valid website
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
                #Filter whitelisted entries
                if filteredWebsite.endswith(whitelistedTLDs) == False and filteredWebsite not in whitelistedWebsites:
                    #Remove echoed entries
                    length = len(filteredWebsite) - 1
                    if length % 2 == 0:
                        midpoint = len(filteredWebsite) // 2
                        if filteredWebsite[:midpoint] == filteredWebsite[midpoint+1:]:
                            filteredWebsite = filteredWebsite[:midpoint]
                    #Check if the website has been listed in previous entries
                    if filteredWebsite not in websiteCache and filteredWebsite != "":
                        websiteCache.append(filteredWebsite)
                        newWebsites.append(filteredWebsite)
    
    return newWebsites

if __name__ == '__main__':
    
    print("Processing FMA!")
    FMAProcessor()
    
    print("Processing ASIC!")
    ASICProcessor()
    
    print("Processing IOSCO!")
    IOSCOProcessor()
           
    with open('scamsList.json', 'w', encoding='utf-8') as file:
            json.dump(scamsList, file, indent = 2)
    