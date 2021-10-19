# Note: Don't delete this, it isn't in current use but it's to deal with future semantics


# Imports and initialisations
import sqlite3
import urllib.request, urllib.parse, urllib.error, ssl, re, json
from urllib.request import urlopen

conn = sqlite3.connect('textCorpus.sqlite')
cur = conn.cursor()

idiom = "jack of all trades"
result = None

# Retrieve the global ID for the idiom
cur.execute( """
SELECT Idiom.id
    FROM Idiom
    WHERE Idiom.idiom = ?""", (idiom , ) )
id = cur.fetchall()[0][0]

# Retrieve the part of speech for the whole idiom
cur.execute( """
SELECT Idiom.global_pos
    FROM Idiom
    WHERE Idiom.idiom = ?""", (idiom , ) )
global_pos = cur.fetchall()[0][0]

# Retrieve the related terms and their types [either 'synonym', 'related_terms', 'see_also','derived_terms' or 'alternative_terms'] as a list of tuples
cur.execute( """
SELECT Related.related, Related.type
    FROM Idiom JOIN Related
    ON Idiom.id = Related.idiom_id
    WHERE Idiom.idiom = ?""", (idiom , ) )
related = cur.fetchall()

# Retrieve the definition(s)
cur.execute( """
SELECT Semantic.definition
    FROM Idiom JOIN Semantic
    ON Idiom.id = Semantic.idiom_id
    WHERE Idiom.idiom = ? AND Semantic.definition IS NOT NULL""", (idiom , ) )
definitions = cur.fetchall()

# Retrieve the example(s)
cur.execute( """
SELECT Semantic.example
    FROM Idiom JOIN Semantic
    ON Idiom.id = Semantic.idiom_id
    WHERE Idiom.idiom = ? AND Semantic.example IS NOT NULL""", (idiom , ) )
examples = cur.fetchall()

# Error checking
print("ID:\n", id, "\n\nGlobal POS:\n", global_pos)

print("\nRelated:")
for i in related:
    print(i[0:2])

print("\nExamples:")
for i in examples:
    print(i[0:2])

print("\nDefinitions:")
for i in definitions:
    print(i[0:2])
