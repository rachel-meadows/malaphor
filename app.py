from operator import index
from flask import Flask, request, render_template, url_for, redirect
from malaphor import generate_malaphor
from markupsafe import escape
import sys

# Creates an instance of the Flask class that will be the WSGI application.
app = Flask(__name__)

# Default malaphor on page load


@app.route("/", methods=['GET', 'POST'])
def home(malaphor=None, currentIdiom=None, idiomMatch=None):
    currentIdiom, idiomMatch, malaphor = generate_malaphor()
    return render_template('index.html', malaphor=malaphor, currentIdiom=currentIdiom, idiomMatch=idiomMatch)


# Clicking 'New malaphor' button generates a new malaphor
def new_malaphor(malaphor=None, currentIdiom=None, idiomMatch=None):
    if request.method == 'GET':
        currentIdiom, idiomMatch, malaphor = generate_malaphor()
        return render_template('index.html', malaphor=malaphor, currentIdiom=currentIdiom, idiomMatch=idiomMatch)


# I want:
# http:domain-path/query?profanityFilter=True&startingIdiom=None
# http:domain-path/query?profanityFilter=False&startingIdiom=None
# http:domain-path/query?profanityFilter=True&startingIdiom=half+a+loaf+is+better+than+none
# http:domain-path/query?profanityFilter=False&startingIdiom=half+a+loaf+is+better+than+none

@app.route("/:profanityFilter", methods=['GET', 'POST'])
def profanityFilter():
    return ("hi ", profanityFilter)

# Queries
# @app.route("/q", methods=['POST'])
# def query():

#     args = request.args
#     print(args, file=sys.stderr)

#     if "profanityFilter" in args:
#         profanityFilter = escape(args.get("profanityFilter"))
#     if "startingIdiom" in args:
#         startingIdiom = escape(args["startingIdiom"])

#     return "No query string received", 200


# @app.route("/profanityFilter", methods=['POST'])
# def profanityFilter(malaphor=None, currentIdiom=None, idiomMatch=None):
#     profanityFilter = request.args.get('profanityFilter')
#     startingIdiom = request.args.get('startingIdiom')
#     if request.method == 'POST':
#         currentIdiom, idiomMatch, malaphor = generate_malaphor(True)
#         return render_template('index.html', malaphor=malaphor, currentIdiom=currentIdiom, idiomMatch=idiomMatch)

if __name__ == '__main__':
    app.run(debug=True)
