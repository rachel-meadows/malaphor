"""

This file downloads content into a text file, which is then used to build an SQLite database.
The file 'malaphor.py' is used to work with these data once extracted.

"""

# Imports and initialisations
import urllib.request, urllib.parse, urllib.error, ssl, re, json, sqlite3
from urllib.request import urlopen
from bs4 import BeautifulSoup
from wiktionaryparser import WiktionaryParser
import time

idiomList = []
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


"""

Uses the local list of idioms created above.
Takes these idioms and uses them to make a SQLite database with key info about each idiom.

"""

# Counter initialisations
alreadyLogged = 0
newLogs = 0
everyTen = 0

conn = sqlite3.connect('textCorpus.sqlite')
cur = conn.cursor()

# Setup the SQLite tables
cur.executescript('''

CREATE TABLE IF NOT EXISTS Idiom (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    idiom   TEXT UNIQUE,
    global_pos   TEXT
);

CREATE TABLE IF NOT EXISTS Related (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    idiom_id    INTEGER,
    related TEXT,
    type TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Semantic (
    id     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    definition   TEXT,
    example        TEXT,
    idiom_id    INTEGER
);

''')

idioms = json.load(open("textCorpus.txt"))

# Set up to parse the HTML as JSON with WiktionaryParser
parser = WiktionaryParser()
parser.set_default_language('english')

# Main loop:
for idiom in idioms:
    print(idiom)

    # See if idiom is already in the SQLite database, and skip if it exists.
    result = None
    cur.execute("select EXISTS(select 1 FROM Idiom WHERE idiom = ? )", (idiom , ))
    result = cur.fetchall()
    idiomInDatabase = result
    if idiomInDatabase[0] == (1,): # There is a record in the database - go to next idiom
        alreadyLogged += 1
        continue

    time.sleep(1) # Reduce load
    try:
        jsonRaw = parser.fetch(idiom.lower())
    except:
        continue
    jsonFormattedStr = json.dumps(jsonRaw, indent=2)
    jsonData = json.loads(jsonFormattedStr)
    # print(jsonFormattedStr) # Uncomment to observe the data

    # Get the variables of interest to be passed into the SQLite tables

    # Idiom table
    try:
        global_pos = jsonData[0]["definitions"][0]["partOfSpeech"]
    except:
        global_pos = ""

    # Semantic table
    definition = []
    # Items like definition, examples etc. have their data added as lists as they have multiple entries.
    # They are transformed into one line per item when added to the database.
    try:
        for i in jsonData[0]["definitions"][0]["text"]:
            definition.append(i)
    except:
        pass

    examples = []
    try:
        for x in jsonData[0]["definitions"][0]["examples"]:
            examples.append(x)
    except:
        pass

    # Related table
    synonyms = []
    try:
        for y in jsonData[0]["definitions"][0]["relatedWords"][0]:
            if jsonData[0]["definitions"][0]["relatedWords"][0][y] == "synonyms":
                for z in jsonData[0]["definitions"][0]["relatedWords"][0]["words"]:
                    z = z.split(", ")
                    for i in z:
                        synonyms.append(i) # This ugly syntax is to avoid a list of lists
    except:
        pass

    see_also = []
    try:
        for y in jsonData[0]["definitions"][0]["relatedWords"][0]:
            if jsonData[0]["definitions"][0]["relatedWords"][0][y] == "see also":
                for z in jsonData[0]["definitions"][0]["relatedWords"][0]["words"]:
                    see_also.append(z)
    except:
        pass

    derived_terms = []
    try:
        for y in jsonData[0]["definitions"][0]["relatedWords"][0]:
            if jsonData[0]["definitions"][0]["relatedWords"][0][y] == "derived terms":
                for z in jsonData[0]["definitions"][0]["relatedWords"][0]["words"]:
                    derived_terms.append(z)
    except:
        pass

    alternative_terms = []
    try:
        for y in jsonData[0]["definitions"][0]["relatedWords"][0]:
            if jsonData[0]["definitions"][0]["relatedWords"][0][y] == "alternative terms":
                for z in jsonData[0]["definitions"][0]["relatedWords"][0]["words"]:
                    alternative_terms.append(z)
    except:
        pass

    related_terms = []
    try:
        for y in jsonData[0]["definitions"][0]["relatedWords"][0]:
            if jsonData[0]["definitions"][0]["relatedWords"][0][y] == "related terms":
                for z in jsonData[0]["definitions"][0]["relatedWords"][0]["words"]:
                    related_terms.append(z)
    except:
        pass

    # Testing: Uncomment for more details about each input
    # print("\n\nIdiom:\n", idiom, "Global POS:\n\n", global_pos, "\n\nDefinition:\n", definition, "\n\nExamples:\n", examples, "\n\nSynonyms:\n", synonyms)


    # Put values in the Idiom table
    cur.execute('''INSERT OR IGNORE INTO Idiom (idiom, global_pos)
        VALUES ( ?, ? )''', ( idiom, global_pos) )


    # Put values in the Related table

    # Put in synonyms
    for i in synonyms:
        cur.execute('SELECT id FROM Idiom WHERE idiom = ? ', (idiom , ))
        idiom_id = cur.fetchone()[0]
        cur.execute('''INSERT OR IGNORE INTO Related (idiom_id, related, type)
            VALUES ( ?, ?, ?)''', ( idiom_id, i, "synonym" ) )

    # Put in "See also"
    for i in see_also:
        cur.execute('SELECT id FROM Idiom WHERE idiom = ? ', (idiom , ))
        idiom_id = cur.fetchone()[0]
        cur.execute('''INSERT OR IGNORE INTO Related (idiom_id, related, type)
            VALUES ( ?, ?, ?)''', ( idiom_id, i, "see_also" ) )

    # Put in Derived terms
    for i in derived_terms:
        cur.execute('SELECT id FROM Idiom WHERE idiom = ? ', (idiom , ))
        idiom_id = cur.fetchone()[0]
        cur.execute('''INSERT OR IGNORE INTO Related (idiom_id, related, type)
            VALUES ( ?, ?, ?)''', ( idiom_id, i, "derived_terms" ) )

    # Put in Alternative terms
    for i in alternative_terms:
        cur.execute('SELECT id FROM Idiom WHERE idiom = ? ', (idiom , ))
        idiom_id = cur.fetchone()[0]
        cur.execute('''INSERT OR IGNORE INTO Related (idiom_id, related, type)
            VALUES ( ?, ?, ?)''', ( idiom_id, i, "alternative_terms" ) )

    # Put in Related terms
    for i in related_terms:
        cur.execute('SELECT id FROM Idiom WHERE idiom = ? ', (idiom , ))
        idiom_id = cur.fetchone()[0]
        cur.execute('''INSERT OR IGNORE INTO Related (idiom_id, related, type)
            VALUES ( ?, ?, ?)''', ( idiom_id, i, "related_terms" ) )


    # Put values in the Semantic table

    # Put in Definitions
    for i in definition:
        cur.execute('SELECT id FROM Idiom WHERE idiom = ? ', (idiom , ))
        idiom_id = cur.fetchone()[0]
        cur.execute('''INSERT OR IGNORE INTO Semantic (idiom_id, definition)
            VALUES ( ?, ?)''', ( idiom_id, i ) )

    # Put in Examples
    for i in examples:
        cur.execute('SELECT id FROM Idiom WHERE idiom = ? ', (idiom , ))
        idiom_id = cur.fetchone()[0]
        cur.execute('''INSERT OR IGNORE INTO Semantic (idiom_id, example )
            VALUES ( ?, ?)''', ( idiom_id, i ) )

    conn.commit()
    newLogs += 1
    everyTen += 1

    if everyTen == 10: # Lets you see that nothing has frozen up.
        print(alreadyLogged, "entries already in database.")
        print(newLogs, "new entries added.")
        everyTen = 0
        time.sleep(5)

print("Done!")