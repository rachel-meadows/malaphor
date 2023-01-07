from nltk.probability import FreqDist
import sqlite3

# These helpers are for actions that only need to happen once, once page load
# i.e. they should not be run on every iteration of generate_malaphor

def get_splitting_words():
    # Set up SQLite connection
    conn = sqlite3.connect('textCorpus.sqlite')
    cur = conn.cursor()

    # Find words that are relatively long, but not unique, within the corpus
    # These generally make better 'splitting words' later on
    cur.execute("""SELECT idiom FROM Idiom""", )
    try:
        idiomList = cur.fetchall()
    except:
        pass
    wordList = []
    for i in idiomList:
        for word in i[0].split():
            wordList.append(word)
    wordFrequency = FreqDist(wordList)
    goodSplittingWords = sorted(w for w in set(wordList) if len(w)
                          > 4 and wordFrequency[w] > 2)
    return goodSplittingWords



def check_for_user_idiom(user_idiom):
    # Set up SQLite connection
    conn = sqlite3.connect('textCorpus.sqlite')
    cur = conn.cursor()

    try:
        cur.execute("""
    SELECT Idiom.idiom
    FROM Idiom
    WHERE Idiom.idiom = ?""", (user_idiom, ))
        idiom = cur.fetchall()[0][0].lower()
        return ['present', idiom]

    except:
            cur.execute("""
        SELECT Idiom.idiom
        FROM Idiom
        WHERE Idiom.idiom LIKE ?""", ("%" + user_idiom + "%", ))
            # ^ Finds any matching sentence fragments with extra words at the beginning or end

            idiom = (cur.fetchall())[0][0].lower()
            return ['partial', idiom]
    return
