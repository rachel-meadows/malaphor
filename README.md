# MALAPHOR GENERATOR

_A malaphor (mixed metaphor) generator to mint new idioms._

## What is a malaphor?
A malaphor is an error in which **two figures of speech are merged**, producing an often nonsensical result.

For example, we can take these idioms:
- "It's not brain science"
- "It's not rocket surgery"
...and recombine them to create the malaphor, "It's not rocket surgery."

A less common malaphor is "We'll burn that bridge when we get to it" (from _"Burn one's bridges"_ and _"We'll cross that bridge when we get to it"_). 

## Why a malaphor generator?
At the time of writing this, there is no generator that generates malaphors from _any_ corpus of data. The only work in this space uses a small handful of 5-10 predefined idioms to generate semi-random recombinations.

This generator scrapes Wiktionary's corpus of [https://en.wiktionary.org/wiki/Category:English_idioms](8000+ idioms) and [https://en.wiktionary.org/wiki/Category:English_proverbs](1,000+ proverbs), which are constantly being updated. The scope of this allows for more possible malaphors to be evaluated, and for rudimentary criteria to be used to 'grade' the outputs before showing the best ones to the user.

These malaphors are entirely novel, which makes them fun - every new generation is a roll of the dice!

_And on that note - please be aware that some of idioms in Wiktionary's corpus contain profanity, which is can be passed on to the malaphors._

## What's the status of this project?
This is a working version of a command-line program that builds a local text file, then generates simple malaphors from that.

I'm in the process of a) using a SQLite database to refine the text output to better reflect semantic content, and b) building a front end for the program so it is accessible to users without having to download this code and re-scrape the data.
