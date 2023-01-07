from helpers import get_splitting_words, check_for_user_idiom

from profanityfilter import ProfanityFilter
pf = ProfanityFilter()
import re
import sqlite3

goodSplittingWords = get_splitting_words()

def generate_malaphor(profanity_filter = True, user_idiom = ""):

    # Set up SQLite connection
    conn = sqlite3.connect('textCorpus.sqlite')
    cur = conn.cursor()

    # If the user has chosen their own starting idiom, check if it is in the database
    if user_idiom:
        # Returns ['present' | 'partial' , 'idiom' ] | [False]
        isPresent = check_for_user_idiom(user_idiom)
        if isPresent[0] == False:
            return('Sorry, that idiom isn\'t in the database.')
        elif isPresent[0] == 'partial':
            return('Sorry, that idiom isn\'t in the database. Did you mean "' + isPresent[1] + '"?')
        else:
            # All references to user_idiom from here on are to an actual record.
            pass

    # Get a random idiom to merge with the current idiom
    def get_random_idiom():
        cur.execute("""
    SELECT idiom FROM Idiom ORDER BY RANDOM() LIMIT 1""", )
        try:
            random_idiom = cur.fetchall()
            random_idiom = random_idiom[0][0]
            return random_idiom
        except:
            pass

    userIdiom = ""

    # Search through all idioms, and find ones that share a word with the current selection
    # This will continue for n iterations before trying again with a new selected_idiom

    def findSharedWord(comparison_idiom, n):
        points = 0
        count = 0
        userIdiomCount = 0
        for word in selected_idiom:
            while True:

                # If the user has selected their own idiom as the selected_idiom
                if userIdiom != "":
                    comparison_idiom = str(get_random_idiom()).split()
                    for comparison_word in comparison_idiom:
                        if comparison_word in selected_idiom:
                            return(comparison_word, comparison_idiom)
                        else:
                            continue
                    userIdiomCount += 1
                    if userIdiomCount >= 9_200:  # Approximate number of unique entries in the database
                        userIdiomCount = 0
                        raise Exception("Sorry, a match can't be found for this idiom.\nIt may be too short / use only unique words.")

                # If the computer selected a random idiom as selected_idiom
                else:

                    # Before looking through a random idiom for shared words, look through related terms
                    cur.execute("""
                SELECT Related.related, Related.type
                    FROM Idiom JOIN Related
                    ON Idiom.id = Related.idiom_id
                    WHERE Idiom.idiom = ?""", (whole_selected_idiom, ))
                    try:
                        related = cur.fetchall()
                    except:
                        pass

                    for comparison_idiom, relatedType in related:
                        # Cut out the optional CONTEXT of the related idiom, which can result in similar outputs - e.g.:
                        # "jump the queue" + "(US) jump the line" --> "(US) jump the queue" (not identified as duplicate)
                        comparison_idiom = re.sub(
                            r"\([^()]*\): ", "", comparison_idiom)
                        comparison_idiom = re.sub(
                            r"\([^()]*\)", "", comparison_idiom)

                        # Skip the current idiom if the profanity filter is on and it contains swear words
                        if profanity_filter == True:
                            profanity = pf.is_profane(str(comparison_idiom))
                            if profanity == True:
                                continue # Keep looking
                            else:
                                pass
                        else:
                            pass

                        # Related items don't have to get a weighted score since they're usually better
                        for comparison_word in comparison_idiom.split():
                            if comparison_word in selected_idiom:
                                return(comparison_word, comparison_idiom.split())
                            else:
                                continue

                    # Points system if no related words that fit
                    comparison_idiom = str(get_random_idiom()).split()

                    for comparison_word in comparison_idiom:
                        if comparison_word in selected_idiom:
                            if profanity_filter == True:
                                profanity = pf.is_profane(str(comparison_idiom))
                                if profanity == True:
                                    continue # Keep looking
                                else:
                                    pass
                            else:
                                pass

                            # Longer idioms are usually more interesting, but they don't both need to be long
                            points += (len(comparison_idiom +
                                           selected_idiom) * 0.3)

                            # There are a LOT of these; they get boring after a while
                            if comparison_word in ["ones", "one's"]:
                                points -= 3

                            # More generic = less interesting
                            if comparison_word not in ["and", "the", "one's", "in", "on", "a", "for", "of", "ones"]:
                                points += 3

                            # These are longer words present in at least 2 idioms
                            if comparison_word in goodSplittingWords:
                                points += 3

                            # More generic = less interesting, and longer words are usually more specialised
                            if len(comparison_word) > 3:
                                points += ((len(comparison_word)) * 0.6)
                            try:
                                if comparison_idiom[comparison_idiom.index(comparison_word) + 1] not in ["the", "one", "one's"]:
                                    # The following criteria only makes sense if the phrase isn't 'in the' etc.
                                    try:
                                        if comparison_idiom[comparison_idiom.index(comparison_word) + 1][0] == selected_idiom[selected_idiom.index(comparison_word) + 1][0]:
                                            # Sounds better if the next word starts with the same letter
                                            if comparison_idiom[comparison_idiom.index(comparison_word) + 1] == selected_idiom[selected_idiom.index(comparison_word) + 1]:
                                                # i.e. they're the same word
                                                points += 4
                                            else:
                                                # If the following word starts with the same letter, yet is NOT that word, it's even better
                                                points += 5
                                    except:  # Some phrases end with the comparison_word, this avoids out of range error
                                        pass
                            except:
                                pass

                        if points >= 9:  # Edit this for more / less strict filtering
                            return(comparison_word, comparison_idiom)
                        else:
                            points = 0
                            continue
                    count += 1
                    if count >= n:
                        points = 0
                        break

    # If no match found after 10 (n) iterations, the current idiom is swapped (as it may consist of unusual / unique words not present in other idioms)
    while True:
        if userIdiom != "":
            selected_idiom = userIdiom.split()
        else:
            whole_selected_idiom = str(get_random_idiom())
            selected_idiom = whole_selected_idiom.split()

        # The second argument is how many tries before swapping idioms
        try:
            matchTuple = findSharedWord("", 10)
        except Exception as inst:
            return inst.args
        if matchTuple != None:
            wordMatch = matchTuple[0]
            matching_idiom = matchTuple[1]
        else:
            continue

        # Locate shared word in each idiom
        selected_idiomIndex = selected_idiom.index(wordMatch)
        new_idiom_index = matching_idiom.index(wordMatch)

        # Usually, swapping a word into the longer sentence makes for a more interesting malaphor.
        # However, this depends on where the matching word is in the sentence. This picks the idiom with the most words BEFORE the matching word.
        if selected_idiomIndex > new_idiom_index:
            starting_idiom = selected_idiom
            ending_idiom = matching_idiom
        # Not doing a random choice if they're equal length since the original idiom was random anyway.
        elif selected_idiomIndex <= new_idiom_index:
            starting_idiom = matching_idiom
            ending_idiom = selected_idiom
        generated_malaphor = (" ".join(starting_idiom[0:starting_idiom.index(
            wordMatch)]) + " " + " ".join(ending_idiom[ending_idiom.index(wordMatch):]))

        # More of the original context is usually funnier, but only if it's a natural progression point
        # I'm using length as a rough heuristic for this (e.g. if the malaphor is already 10+ words, it probably doesn't need a wraparound end)
        if len(generated_malaphor) <= 10:
            if len(generated_malaphor.split()) < len(starting_idiom):
                addition = starting_idiom[len(generated_malaphor.split()):]
                generated_malaphor = generated_malaphor + " " + " ".join(addition)

            elif len(generated_malaphor.split()) < len(ending_idiom):
                addition = ending_idiom[len(generated_malaphor.split()):]
                generated_malaphor = generated_malaphor + " ".join(addition)
        else:
            pass

        # Get rid of duplicates
        if generated_malaphor.strip() == str(" ".join(starting_idiom)) or generated_malaphor.strip() == str(" ".join(ending_idiom)):
            continue
        # If the match is the first or last word within a short sentence, it's usually boring
        # E.g. "take down a notch" + "come down the pike" --> "come down a notch"
        elif ((selected_idiom[-1] == wordMatch and selected_idiom[0] == wordMatch) and (len(matching_idiom) <= 4)):
            continue
        else:
            break

    selected_idiom = " ".join(selected_idiom)
    matching_idiom = " ".join(matching_idiom)

    # More personal = more entertaining
    selected_idiom = selected_idiom.replace(" one's ", " your ")
    matching_idiom = matching_idiom.replace(" one's ", " your ")
    generated_malaphor = generated_malaphor.replace(" one's ", " your ")

    return selected_idiom, matching_idiom, generated_malaphor


# For testing without frontend
# The starting idiom choice and profanity filter work here - just need frontend integration
# generated_malaphor = generated_malaphor(True, "")
# print(generated_malaphor)