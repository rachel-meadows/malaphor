from flask import Flask
from flask import render_template
from flask import Flask, jsonify, request, render_template
from malaphor import generate_malaphor

# Creates an instance of the Flask class that will be the WSGI application.
app = Flask(__name__)


@app.route("/")
# Default malaphor on page load
def show_malaphor(malaphor=None, currentIdiom=None, idiomMatch=None):
    currentIdiom, idiomMatch, malaphor = generate_malaphor()
    return render_template('index.html', malaphor=malaphor, currentIdiom=currentIdiom, idiomMatch=idiomMatch)

# Clicking 'New malaphor' button generates a new malaphor


@app.route("/")
def new_malaphor(malaphor=None, currentIdiom=None, idiomMatch=None):
    if request.method == 'GET':
        currentIdiom, idiomMatch, malaphor = generate_malaphor()
        return render_template('index.html', malaphor=malaphor, currentIdiom=currentIdiom, idiomMatch=idiomMatch)


if __name__ == '__main__':
    app.run(debug=True)
