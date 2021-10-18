"""

Malaphor generator based on Wiktionary's list of idioms.
The file 'simplemalaphor3.py' is used to work with these data once extracted.

"""

# Imports and initialisations
import urllib.request, urllib.parse, urllib.error, ssl, re, json
from urllib.request import urlopen
from bs4 import BeautifulSoup

# Set up to parse the HTML with BeautifulSoup
url = "https://en.wiktionary.org/wiki/Category:English_idioms"
html = urlopen(url).read()
soup = BeautifulSoup(html, "html.parser")

# Get the links to the items in the Wiktionary Idioms table of contents (as it is split into multiple pages)
tags = soup.find_all(href = re.compile("English_idioms\&from=[a-zA-Z][a-zA-Z]"))
contents = []
for link in tags:
    contents.append((link['href']))
contentsCount = len(contents) #676 unique pages of idioms at the moment!
# TODO: Automate intermittent updates to the idiom list.

# Main loop to iterate through all URLs in the Wiktionary directory of idioms, and add their contents to a local txt file
pageCount = 0 # How many index directory pages have been iterated through
idiomList = []
while True:
    if pageCount <= (contentsCount -1):
        # Get the link to a new contents page (equivalent id to [aa] - [zz])
        currentContents = tags[pageCount]
        print(currentContents.get('href', None)) # For error checking

        # Follow the link
        newUrl = (currentContents.get('href', None))

        # Change URL and re-parse the HTML with BeautifulSoup
        html = urlopen(newUrl).read()
        soup = BeautifulSoup(html, "html.parser")

        # Find and extract the textual idioms, starting from this div
        containingDiv = soup.find("div", {"class": "mw-category-group"})

        # finding all li tags following that div, and add the text within it to list
        if containingDiv != None: # Some of the Wiktionary directory pages (e.g. yp) exist but are blank
            for li in containingDiv.find_all("li"):
                idiomList.append(li.text)
        else:
            pass

        pageCount += 1 # Iterate how many URLs of the TOTAL directory have been parsed
        continue

    else: #pageCount has reached the end of directory list
        break

# Write the list of idioms to a local output file for faster processing
with open('idiomList.txt', 'w') as filehandle:
    json.dump(idiomList, filehandle)
filehandle.close()

# Now see simplemalaphor3.py for text processing and working with the data.
