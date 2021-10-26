# Imports and initialisations
import json, random, nltk, os, time, sqlite3, urllib.request, urllib.parse, urllib.error, ssl, re, json
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
from urllib.request import urlopen
from profanityfilter import ProfanityFilter
pf = ProfanityFilter()

# System call so colour works in console
os.system("")

# Command line colour styling
class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    RESET = '\033[0m'

# Set up SQLite connection
conn = sqlite3.connect('textCorpus.sqlite')
cur = conn.cursor()
result = None

# Find words that are relatively long, but not unique, within the corpus
# These generally make better 'splitting words' later on
cur.execute( """
    SELECT idiom FROM Idiom""", )
try:
    idiomList = cur.fetchall()
except:
    pass
wordList = []
for i in idiomList:
    for word in i[0].split():
        wordList.append(word)
wordFrequency = FreqDist(wordList)
specialWords = sorted(w for w in set(wordList) if len(w) > 4 and wordFrequency[w] > 2)

# Get a random idiom to merge with the current idiom
def getRandomIdiom():
    cur.execute( """
    SELECT idiom FROM Idiom ORDER BY RANDOM() LIMIT 1""", )
    try:
        randomIdiom = cur.fetchall()
        randomIdiom = randomIdiom[0][0]
        return randomIdiom
    except:
        pass

userIdiom = ""
# Search through all idioms, and find ones that share a word with the current selection
# This will continue for n iterations before trying again with a new currentIdiom
def findSharedWord(comparisonIdiom, n):
    points = 0
    count = 0
    userIdiomCount = 0
    for word in currentIdiom:
        while True:

            # If the user has selected their own idiom as the currentIdiom
            if userIdiom != "":
                comparisonIdiom = str( getRandomIdiom() ).split()
                for comparisonWord in comparisonIdiom:
                    if comparisonWord in currentIdiom:
                        return(comparisonWord, comparisonIdiom)
                    else:
                        continue
                userIdiomCount += 1
                if userIdiomCount >= 9_200: # Approximate number of unique entries in the database
                    print(style.RED + "\nSorry, a match can't be found for this idiom.\nIt may be too short / use only unique words.\n\n" + style.RESET)
                    userIdiomCount = 0
                    quit()

            # If the computer selected a random idiom as currentIdiom
            else:

                # Before looking through a random idiom for shared words, look through related terms
                cur.execute( """
                SELECT Related.related, Related.type
                    FROM Idiom JOIN Related
                    ON Idiom.id = Related.idiom_id
                    WHERE Idiom.idiom = ?""", ( wholeCurrentIdiom, ) )
                try:
                    related = cur.fetchall()
                except:
                    pass
                
                # Cut out the optional CONTEXT of the related idiom, which can result in similar outputs - e.g.:
                # "jump the queue" + "(US) jump the line" --> "(US) jump the queue" (not identified as duplicate)
                for comparisonIdiom, relatedType in related:
                    comparisonIdiom = re.sub(r"\([^()]*\): ", "", comparisonIdiom)
                    comparisonIdiom = re.sub(r"\([^()]*\)", "", comparisonIdiom)

                    # Skip the current idiom if the profanity filter is on and it contains swear words
                    if profanityFilter == True:
                        profanity = pf.is_profane(str(comparisonIdiom))
                        if profanity == True:
                            continue
                        else:
                            pass
                    else:
                        pass
                    
                    # Related items don't have to get a weighted score since they're usually better
                    for comparisonWord in comparisonIdiom.split():      
                        if comparisonWord in currentIdiom:
                            return(comparisonWord, comparisonIdiom.split())
                        else:
                            continue

                # Points system if no related words that fit
                comparisonIdiom = str( getRandomIdiom() ).split()
                for comparisonWord in comparisonIdiom:
                    if comparisonWord in currentIdiom:
                        if profanityFilter == True:
                            profanity = pf.is_profane(str(comparisonIdiom))
                            if profanity == True:
                                continue
                            else:
                                pass
                        else:
                            pass
                        
                        # Longer idioms are usually more interesting, but they don't both need to be long
                        points += (len(comparisonIdiom + currentIdiom) * 0.3) 

                        # There are a LOT of these; they get boring after a while
                        if comparisonWord in ["ones", "one's"]: 
                            points -= 3
                        
                        # More generic = less interesting
                        if comparisonWord not in ["and", "the", "one's", "in", "on", "a", "for", "of", "ones"]: # 
                            points += 3

                        # These are longer words present in at least 2 idioms
                        if comparisonWord in specialWords: 
                            points += 3
                        
                        # More generic = less interesting, and longer words are usually more specialised
                        if len(comparisonWord) > 3: 
                            points += ( (len(comparisonWord)) * 0.6 )
                        try:
                            if comparisonIdiom[comparisonIdiom.index(comparisonWord) + 1] not in ["the", "one", "one's"]:
                                # The following criteria only makes sense if the phrase isn't 'in the' etc.
                                try:
                                    if comparisonIdiom[comparisonIdiom.index(comparisonWord) + 1][0] == currentIdiom[currentIdiom.index(comparisonWord) + 1][0]:
                                        # Sounds better if the next word starts with the same letter
                                        if comparisonIdiom[comparisonIdiom.index(comparisonWord) + 1] == currentIdiom[currentIdiom.index(comparisonWord) + 1]:
                                            #i.e. they're the same word
                                            points += 4
                                        else:
                                            # If the following word starts with the same letter, yet is NOT that word, it's even better
                                            points += 5
                                except: # Some phrases end with the comparisonWord, this avoids out of range error
                                    pass
                        except:
                            pass

                    if points >= 9: # Edit this for more / less strict filtering
                        return(comparisonWord, comparisonIdiom)
                    else:
                        points = 0
                        continue
                count += 1
                if count >= n:
                    points = 0
                    break

while True:
    userChoice = input("Do you want to submit your own idiom? (y/n)\n")
    if userChoice.lower() == "y":
        userChoice = True
        userIdiom = str(input("\nWhat idiom are you looking for?\n").lower())

        # Retrieve the name of the idiom from the database
        try:
            cur.execute( """
            SELECT Idiom.idiom
            FROM Idiom
            WHERE Idiom.idiom = ?""", (userIdiom, ) )
            name = cur.fetchall()[0][0].lower()
            break

        except:
            try:
                cur.execute("""
                SELECT Idiom.idiom
                FROM Idiom
                WHERE Idiom.idiom LIKE ?""", ( "%" + userIdiom + "%", ) )
                # ^ Finds any matching sentence fragments with extra words at the beginning or end

                name = (cur.fetchall())[0][0].lower()
                print("Looks like Wiktionary doesn't have that idiom. However, it does have '" + name + "'.\nIs that what you were looking for? (y/n)")
                matchCorrect = input()
                if matchCorrect.lower() == "y":
                    userIdiom = name
                    break
                elif matchCorrect.lower() == "n":
                    userIdiom = ""
                    continue
                else:
                    print("Please type 'y' or 'n'.")
                    continue
            except:
                print("\nLooks like Wiktionary doesn't have that idiom - you might want to:\n- Check your spelling\n- Try another idiom\n- Let the program choose an idiom\n")
                userIdiom = ""
                continue
    elif userChoice.lower() == "n":
        userChoice = False
        break
    else:
        print("Please type 'y' or 'n'.")
        continue

# Check if the user wants a profanity filter on
while True:
    profanity = input("Do you want a profanity filter applied? (y/n)\n")
    if profanity.lower() == "y":
        profanityFilter = True
        print("\nYou got it! Some things may slip by the filter, but idioms containing common swear words have been removed.\n")
        break
    elif profanity.lower() == "n":
        profanityFilter = False
        break
    else:
        print("Please type 'y' or 'n'.")
        continue

# If no match found after 10 (n) iterations, the current idiom is swapped (as it may consist of unusual / unique words not present in other idioms)
while True:
    if userIdiom != "":
        currentIdiom = userIdiom.split()
    else:
        wholeCurrentIdiom = str( getRandomIdiom() )
        currentIdiom = wholeCurrentIdiom.split()

    matchTuple = findSharedWord("", 10) # The second argument is how many tries before swapping idioms 
    if matchTuple != None:
        wordMatch = matchTuple[0]
        idiomMatch = matchTuple[1]
    else:
        continue

    # Locate shared word in each idiom
    currentIdiomIndex = currentIdiom.index(wordMatch)
    newIdiomIndex = idiomMatch.index(wordMatch)

    # Usually, swapping a word into the longer sentence makes for a more interesting malaphor.
    # However, this depends on where the matching word is in the sentence. This picks the idiom with the most words BEFORE the matching word.
    if currentIdiomIndex > newIdiomIndex:
        startingIdiom = currentIdiom
        endingIdiom = idiomMatch
    elif currentIdiomIndex <= newIdiomIndex: # Not doing a random choice if they're equal length since the original idiom was random anyway.
        startingIdiom = idiomMatch
        endingIdiom = currentIdiom
    malaphor = (" ".join(startingIdiom[0:startingIdiom.index(wordMatch)]) + " " + " ".join(endingIdiom[endingIdiom.index(wordMatch):]))

    # More of the original context is usually funnier, but only if it's a natural progression point
    # I'm using length as a rough heuristic for this (e.g. if the malaphor is aready 10+ words, it probably doesn't need a wraparound end)
    if len(malaphor) <= 10:
        if len(malaphor.split()) < len(startingIdiom):
            addition = startingIdiom [ len(malaphor.split()) : ]
            malaphor = malaphor + " " + " ".join(addition)

        elif len(malaphor.split()) < len(endingIdiom):
            addition = endingIdiom [ len(malaphor.split()) : ]
            malaphor = malaphor + " ".join(addition)
    else:
        pass

    # Get rid of duplicates
    if malaphor.strip() == str(" ".join(startingIdiom)) or malaphor.strip() == str(" ".join(endingIdiom)):
        continue
    # If the match is the first or last word within a short sentence, it's usually boring
    # E.g. "take down a notch" + "come down the pike" --> "come down a notch"
    elif ( (currentIdiom[-1] == wordMatch and currentIdiom[0] == wordMatch) and (len(idiomMatch) <= 4) ):
        continue
    else:
        break

    if "one's" in malaphor:
        malaphor = malaphor.replace(" one's ", " your ") # More personal = more entertaining

print("\nThe idioms being merged are:\n    " + style.CYAN + " ".join(currentIdiom), "\n   ", " ".join(idiomMatch) + style.RESET)

print("\nThe malaphor:\n    " + style.GREEN + malaphor + style.RESET)
