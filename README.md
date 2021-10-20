# MALAPHOR GENERATOR

_A malaphor (mixed metaphor) generator to mint new idioms._

## What is a malaphor?
A malaphor is an error in which **two figures of speech are merged**, producing an often nonsensical result.

For example, we can take these idioms:
- "It's not brain science"
- "It's not rocket surgery"

...and recombine them to create the malaphor, "**It's not rocket surgery.**"

Here's another example:
- "Burn your bridges" (idiom)
- "We'll cross that bridge when we get to it" (idiom)

..."**We'll burn that bridge when we get to it**" (malaphor!)

## Why a malaphor generator?
At the time of writing this, there is no generator that generates malaphors from _any_ corpus of data. The only work in this space uses a small handful of predefined idioms to generate semi-random recombinations.

This generator scrapes Wiktionary's corpus of [8000+ idioms](https://en.wiktionary.org/wiki/Category:English_idioms) and [1,000+ proverbs](https://en.wiktionary.org/wiki/Category:English_proverbs), which are constantly being updated.

The scope of this allows for more possible malaphors to be evaluated, and for criteria to 'grade' the outputs before showing the best ones to the user.

These malaphors are entirely novel, which makes them fun - every new generation is a roll of the dice!*

<sub>_*And on that note - please be aware some idioms in Wiktionary's corpus contain profanity, which can be passed on to the malaphors. At some point [I'll make an optional toggle](https://github.com/rachel-meadows/malaphor/issues/8#issue-1028591792) to filter these out._</sub>


## What's the status of this project?
This is a working version of a command-line program that builds a local text file and an SQLite database, then generates simple malaphors from these.

I'm in the process of a) using the database to refine the text output to better reflect semantic content, and b) building a front end for the program so it is accessible to users without having to download this code and re-scrape the data.

## Fun: Examples from the program so far
Here are some of the script's better malaphors:

**The idioms being merged:**
    clear cut 
    cut and dried

**The resulting malaphor:**
    clear cut and dried

**The idioms being merged:**
    strike while the iron is hot 
    make hay while the sun shines

**The resulting malaphor:**
    make hay while the iron is hot

**The idioms being merged:**
    put one's name in the hat 
    throw one's hat in the ring

**The resulting malaphor:**
    throw one's name in the hat