from malaphor import generate_malaphor

from operator import index
from flask import Flask, request, render_template

# Creates an instance of the Flask class that will be the WSGI application.
app = Flask(__name__)

# Default malaphor on page load
@app.route("/", methods=['GET', 'POST'])
def home(currentIdiom = None, idiomMatch = None, malaphor = None):
    currentIdiom, idiomMatch, malaphor = generate_malaphor(True, "")
    return render_template('index.html', currentIdiom = currentIdiom, idiomMatch = idiomMatch,  malaphor = malaphor)


# Clicking 'New malaphor' button generates a new malaphor
def new_malaphor(currentIdiom = None, idiomMatch = None, malaphor = None):
    if request.method == 'GET':
        currentIdiom, idiomMatch, malaphor = generate_malaphor(True, "")
        return render_template('index.html', currentIdiom = currentIdiom, idiomMatch = idiomMatch,  malaphor = malaphor)

# if __name__ == '__main__':
#     app.run(debug=False)
