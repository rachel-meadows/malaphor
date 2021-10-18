"""

Malaphor generator based on Wiktionary's list of idioms and proverbs.
Even though the content contains both idioms and proverbs, they will all be called 'Idioms' in variable names for simplicity's sake.

This file downloads content into a text file, which is then used to build an SQLite database.
The file 'Malaphor.py' is used to work with these data once extracted.

"""

# Imports and initialisations
import urllib.request, urllib.parse, urllib.error, ssl, re, json
from urllib.request import urlopen
from bs4 import BeautifulSoup

def contentsIterator (url, REToFindLinks):

    """
    For the relevant starting pages, loop through tables of contents and find page URLs, then find content on those pages.
    """

    # Set up to parse the HTML with BeautifulSoup
    html = urlopen(url).read()
    soup = BeautifulSoup(html, "html.parser")

    # Get the links to the items in the Wiktionary Idioms / Proverbs table of contents (as both are split into multiple pages)
    tags = soup.find_all(href = re.compile(REToFindLinks))
    contents = []
    for link in tags:
        contents.append((link['href']))
    contentsCount = len(contents)

    # Main loop to iterate through all URLs in the index, and add their contents to a local txt file.
    pageCount = 0 # Number of index directory iterated through
    idiomList = []
    while True:
        if pageCount <= (contentsCount -1):
            # Get the link to a new contents page
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
            if containingDiv != None: # Some of the Wiktionary directory pages (e.g. "yp") exist but are blank
                for li in containingDiv.find_all("li"):
                    idiomList.append(li.text)
            else:
                pass

            pageCount += 1 # Iterate how many URLs of the directory INDEX have been parsed
            continue

        else: # pageCount has reached the end of directory list
            break

    # Write the list of idioms to a local output file for faster processing
    with open('textCorpus.txt', 'w') as filehandle:
        json.dump(idiomList, filehandle)
    filehandle.close()


# Invoke the function for Wiktionary's list of idioms
contentsIterator("https://en.wiktionary.org/wiki/Category:English_idioms", "English_idioms\&from=[a-zA-Z][a-zA-Z]")

# Invoke the function for Wiktionary's list of proverbs
contentsIterator("https://en.wiktionary.org/wiki/Category:English_proverbs", "English_proverbs&from=[a-zA-Z]")

# Now see malaphor.py for text processing and working with the data.