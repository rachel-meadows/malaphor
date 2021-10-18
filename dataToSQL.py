<<<<<<< HEAD
"""

Uses the local list of idioms created from Wiktionary using getIdioms.py as a reference.
Takes these idioms and uses them to make a SQLite database with key info about each idiom.
The file 'simpleMalaphor3.py' is used to work with these data once extracted.

"""

# Imports and counter initialisations
import json
import sqlite3
import urllib.request, urllib.parse, urllib.error, ssl, re, json
from urllib.request import urlopen
from bs4 import BeautifulSoup
from wiktionaryparser import WiktionaryParser
import time
alreadyLogged = 0
newLogs = 0
everyTen = 0

conn = sqlite3.connect('malaphortest.sqlite')
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

idiomList = open("idiomList.txt", "r")
idioms = json.load(open("idiomList.txt"))

# Set up to parse the HTML as JSON with WiktionaryParser
parser = WiktionaryParser()
parser.set_default_language('english')

# Main loop:
for idiom in idioms:
    print(idiom)

    # See if idiom is already in the database, and skip if it is.
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
    definition = [] # List due to multiple lines
    try:
        for i in jsonData[0]["definitions"][0]["text"]:
            definition.append(i)
    except:
        pass

    examples = [] # List due to multiple lines
    try:
        for x in jsonData[0]["definitions"][0]["examples"]:
            examples.append(x)
    except:
        pass

    # Related table
    synonyms = [] # List due to multiple lines
    try:
        for y in jsonData[0]["definitions"][0]["relatedWords"][0]:
            if jsonData[0]["definitions"][0]["relatedWords"][0][y] == "synonyms":
                for z in jsonData[0]["definitions"][0]["relatedWords"][0]["words"]:
                    z = z.split(", ")
                    for i in z:
                        synonyms.append(i) #This ugly syntax is to avoid a list of lists
    except:
        pass

    see_also = [] # List due to multiple lines
    try:
        for y in jsonData[0]["definitions"][0]["relatedWords"][0]:
            if jsonData[0]["definitions"][0]["relatedWords"][0][y] == "see also":
                for z in jsonData[0]["definitions"][0]["relatedWords"][0]["words"]:
                    see_also.append(z)
    except:
        pass

    derived_terms = [] # List due to multiple lines
    try:
        for y in jsonData[0]["definitions"][0]["relatedWords"][0]:
            if jsonData[0]["definitions"][0]["relatedWords"][0][y] == "derived terms":
                for z in jsonData[0]["definitions"][0]["relatedWords"][0]["words"]:
                    derived_terms.append(z)
    except:
        pass

    alternative_terms = [] # List due to multiple lines
    try:
        for y in jsonData[0]["definitions"][0]["relatedWords"][0]:
            if jsonData[0]["definitions"][0]["relatedWords"][0][y] == "alternative terms":
                for z in jsonData[0]["definitions"][0]["relatedWords"][0]["words"]:
                    alternative_terms.append(z)
    except:
        pass

    related_terms = [] # List due to multiple lines
    try:
        for y in jsonData[0]["definitions"][0]["relatedWords"][0]:
            if jsonData[0]["definitions"][0]["relatedWords"][0][y] == "related terms":
                for z in jsonData[0]["definitions"][0]["relatedWords"][0]["words"]:
                    related_terms.append(z)
    except:
        pass

    # Uncomment for more details about each input
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

    if everyTen == 10:
        print(alreadyLogged, "entries already in database.")
        print(newLogs, "new entries added.")
        everyTen = 0
        time.sleep(5)

print("Done!")
=======
"""

Uses the local list of idioms created from Wiktionary using getIdioms.py as a reference.
Takes these idioms and uses them to make a SQLite database with key info about each idiom.
The file 'simpleMalaphor3.py' is used to work with these data once extracted.

"""

# Imports and counter initialisations
import json
import sqlite3
import urllib.request, urllib.parse, urllib.error, ssl, re, json
from urllib.request import urlopen
from bs4 import BeautifulSoup
from wiktionaryparser import WiktionaryParser
import time
alreadyLogged = 0
newLogs = 0
everyTen = 0

conn = sqlite3.connect('malaphortest.sqlite')
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

idiomList = open("idiomList.txt", "r")
idioms = json.load(open("idiomList.txt"))

# Set up to parse the HTML as JSON with WiktionaryParser
parser = WiktionaryParser()
parser.set_default_language('english')

# Main loop:
for idiom in idioms:
    print(idiom)

    # See if idiom is already in the database, and skip if it is.
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
    definition = [] # List due to multiple lines
    try:
        for i in jsonData[0]["definitions"][0]["text"]:
            definition.append(i)
    except:
        pass

    examples = [] # List due to multiple lines
    try:
        for x in jsonData[0]["definitions"][0]["examples"]:
            examples.append(x)
    except:
        pass

    # Related table
    synonyms = [] # List due to multiple lines
    try:
        for y in jsonData[0]["definitions"][0]["relatedWords"][0]:
            if jsonData[0]["definitions"][0]["relatedWords"][0][y] == "synonyms":
                for z in jsonData[0]["definitions"][0]["relatedWords"][0]["words"]:
                    z = z.split(", ")
                    for i in z:
                        synonyms.append(i) #This ugly syntax is to avoid a list of lists
    except:
        pass

    see_also = [] # List due to multiple lines
    try:
        for y in jsonData[0]["definitions"][0]["relatedWords"][0]:
            if jsonData[0]["definitions"][0]["relatedWords"][0][y] == "see also":
                for z in jsonData[0]["definitions"][0]["relatedWords"][0]["words"]:
                    see_also.append(z)
    except:
        pass

    derived_terms = [] # List due to multiple lines
    try:
        for y in jsonData[0]["definitions"][0]["relatedWords"][0]:
            if jsonData[0]["definitions"][0]["relatedWords"][0][y] == "derived terms":
                for z in jsonData[0]["definitions"][0]["relatedWords"][0]["words"]:
                    derived_terms.append(z)
    except:
        pass

    alternative_terms = [] # List due to multiple lines
    try:
        for y in jsonData[0]["definitions"][0]["relatedWords"][0]:
            if jsonData[0]["definitions"][0]["relatedWords"][0][y] == "alternative terms":
                for z in jsonData[0]["definitions"][0]["relatedWords"][0]["words"]:
                    alternative_terms.append(z)
    except:
        pass

    related_terms = [] # List due to multiple lines
    try:
        for y in jsonData[0]["definitions"][0]["relatedWords"][0]:
            if jsonData[0]["definitions"][0]["relatedWords"][0][y] == "related terms":
                for z in jsonData[0]["definitions"][0]["relatedWords"][0]["words"]:
                    related_terms.append(z)
    except:
        pass

    # Uncomment for more details about each input
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

    if everyTen == 10:
        print(alreadyLogged, "entries already in database.")
        print(newLogs, "new entries added.")
        everyTen = 0
        time.sleep(5)

print("Done!")
>>>>>>> 510bae5e572ef904aba45f8210778f689e0e1c85
