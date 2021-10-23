# Imports and initialisations
import json
import random
import nltk
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
import os
import time
import sqlite3
import urllib.request, urllib.parse, urllib.error, ssl, re, json
from urllib.request import urlopen
from profanityfilter import ProfanityFilter
pf = ProfanityFilter()

# System call so colour works in console
os.system("")

# Class of different styles
class style():
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    UNDERLINE = '\033[4m'
    RESET = '\033[0m'

conn = sqlite3.connect('textCorpus.sqlite')
cur = conn.cursor()
result = None

userIdiom = ""

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

# Get a random idiom to compare against
def randomIdiom(randomIdiom):

    cur.execute( """
    SELECT idiom FROM Idiom ORDER BY RANDOM() LIMIT 1""", )
    try:
        randomIdiom = cur.fetchall()
        randomIdiom = randomIdiom[0][0]
        return randomIdiom
    except:
        pass

# Search through all idioms and find ones that share a word with the current selection
def findWord(comparisonIdiom, n):
    """
    Looks through n other idioms until it finds a word the same or n is up
    """
    points = 0
    count = 0
    userIdiomCount = 0
    for word in currentIdiom:
        while True:

            # If the user has selected an idiom
            if userIdiom != "":
                comparisonIdiom = str( randomIdiom(randomIdiom) ).split()
                for comparisonWord in comparisonIdiom:
                    if comparisonWord in currentIdiom:
                        return(comparisonWord, comparisonIdiom)
                    else:
                        continue
                userIdiomCount += 1
                if userIdiomCount >= 8000:
                    print(style.RED + "\nSorry, a match can't be found for this idiom.\nIt may be too short / use only unique words.\n\n" + style.RESET)
                    userIdiomCount = 0
                    quit()

            # If the computer is selecting a random idiom
            else:

                # Before selecting a random one, look for semantically related ones
                # i.e. Retrieve the related terms and their types [either 'synonym', 'related_terms', 'see_also','derived_terms' or 'alternative_terms'] as a list of tuples

                cur.execute( """
                SELECT Related.related, Related.type
                    FROM Idiom JOIN Related
                    ON Idiom.id = Related.idiom_id
                    WHERE Idiom.idiom = ?""", ( wholeCurrentIdiom, ) )
                try:
                    related = cur.fetchall()
                    # Error checking
                    # print("Idiom:\n", wholeCurrentIdiom,  "\nRelated:\n", related)
                except:
                    pass

                for comparisonIdiom, relatedType in related:
                    # This regex stops the context of the related idiom being given, which often results in the context being merged with the original idiom to make boring outputs / doubles like:
                    # "jump the queue" + "(US) jump the line" --> "(US) jump the queue"
                    comparisonIdiom = re.sub(r"\([^()]*\): ", "", comparisonIdiom)
                    comparisonIdiom = re.sub(r"\([^()]*\)", "", comparisonIdiom)

                    if profanityFilter == True:
                        profanity = pf.is_profane(str(comparisonIdiom))
                        if profanity == True:
                            continue
                        else:
                            pass
                    else:
                        pass

                    for comparisonWord in comparisonIdiom.split():      
                        if comparisonWord in currentIdiom:
                        # Error checking
                        #print("\n\nOH ME OH MY A TEST CASE\n\nCurrent idiom\n", currentIdiom, "\nComparison word:\n", comparisonWord, "\nComparisonIdiom\n", comparisonIdiom)
                            return(comparisonWord, comparisonIdiom.split())
                        else:
                            continue

                # Points system if no related words that fit
                comparisonIdiom = str( randomIdiom(randomIdiom) ).split()
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

                        points += (len(comparisonIdiom + currentIdiom) * 0.3) # Longer idioms are usually more interesting, but they don't both need to be long
                        if comparisonWord in ["ones", "one's"]: # There are a LOT of these, they get boring after a while
                            points -= 3
                        if comparisonWord not in ["and", "the", "one's", "in", "on", "a", "for", "of", "ones"]: # More generic = less interesting
                            points += 3
                        if comparisonWord in specialWords: # These are longer words shared across more idioms
                            points += 4
                        if len(comparisonWord) > 3: # More generic = less interesting, and longer words are usually more specialised
                            points += ( (len(comparisonWord)) * 0.7 )
                        try:
                            if comparisonIdiom[comparisonIdiom.index(comparisonWord) + 1] not in ["the", "one", "one's"]:
                                # The following criteria only makes sense if it's not 'in the' etc.
                                try:
                                    if comparisonIdiom[comparisonIdiom.index(comparisonWord) + 1][0] == currentIdiom[currentIdiom.index(comparisonWord) + 1][0]: # Sounds better if the next word starts with the same letter
                                        if comparisonIdiom[comparisonIdiom.index(comparisonWord) + 1] == currentIdiom[currentIdiom.index(comparisonWord) + 1]: #i.e. they're the same word
                                            points += 4
                                        else: # If the following word starts with the same letter, but is not that word, it's better
                                            points += 5
                                except: # Some phrases end with the comparisonWord, this avoids out of range error
                                    pass
                        except: # Some phrases end with the comparisonWord, this avoids out of range error
                            pass

                    if points >= 10: # Edit this for more / less strict filtering
                        return(comparisonWord, comparisonIdiom)
                    else:

                        # This section can be uncommented to see if the current model looks fair (i.e. "are 'good' idioms being prioritised?")
                        """
                        if points > 1: #i.e. at least one word matches
                            print("\nThe idioms being merged are:\n    " + style.RED + " ".join(currentIdiom) + "\n    " + " ".join(comparisonIdiom) + \
                            style.RESET + "\n" + "Shared word:\n    " + style.RED + comparisonWord + style.RESET + "\n" + "\nPOINTS:\n    " + \
                            style.BLUE , round(points,2) , style.RESET + "\n")
                            time.sleep(2)
                        """

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

        # Retrieve the name of the idiom
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
                WHERE Idiom.idiom LIKE ?""", ( "%" + userIdiom + "%", ) ) # Finds sentence fragment with extra words at start or end

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
        wholeCurrentIdiom = str( randomIdiom(randomIdiom) )
        currentIdiom = wholeCurrentIdiom.split()

    matchTuple = findWord("", 10)

    if matchTuple != None:
        wordMatch = matchTuple[0]
        idiomMatch = matchTuple[1]
    else:
        continue

    # Locate shared word in each idiom
    currentIdiomIndex = currentIdiom.index(wordMatch)
    newIdiomIndex = idiomMatch.index(wordMatch)

    # Usually, swapping a word into the longer sentence makes for a more interesting malaphor.
    # However, this is dependent on where the matching word is in the sentence. This picks the idiom with the most words before the matching word to start.
    if currentIdiomIndex > newIdiomIndex:
        startingIdiom = currentIdiom
        endingIdiom = idiomMatch
    elif currentIdiomIndex <= newIdiomIndex: # Not doing a random choice if they're equal length since the original idiom was random anyway.
        startingIdiom = idiomMatch
        endingIdiom = currentIdiom
    malaphor = (" ".join(startingIdiom[0:startingIdiom.index(wordMatch)]) + " " + " ".join(endingIdiom[endingIdiom.index(wordMatch):]))

    # More of the original context is usually funnier, but only if it's a natural progression point
    # I'm using length as a rough heuristic for this (e.g. if the malaphor is aready 10+ words, it probably doesn't need the wraparound end)
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
    # print("Malaphor:", malaphor, "\nStarting idiom:", str(" ".join(startingIdiom)), "\nEnding idiom:", str(" ".join(endingIdiom)))  # Error checking
    if malaphor.strip() == str(" ".join(startingIdiom)) or malaphor.strip() == str(" ".join(endingIdiom)):
        continue
    # If the match is the first or last word with a short sentence, it's usually boring
    # E.g. "take down a notch" + "come down the pike" --> "come down a notch"
    elif ( (currentIdiom[-1] == wordMatch and currentIdiom[0] == wordMatch) and (len(idiomMatch) <= 4) ):
        continue
    else:
        break

    if "one's" in malaphor:
        malaphor = malaphor.replace(" one's ", " your ") # More personal = more entertaining

print("\nThe idioms being merged are:\n    " + style.CYAN + " ".join(currentIdiom), "\n   ", " ".join(idiomMatch) + style.RESET)

print("\nThe malaphor:\n    " + style.GREEN + malaphor + style.RESET)