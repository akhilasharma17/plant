from flask import Flask, template

app = Flask(__name__)


# homepage
@app.route('/')
def homepage():
    return template("home.html")


# plants page
@app.route('/plant/<int:id>')
def plant(id):
    return template("plant.html")


# about/contact information page
@app.route('/contact')
def contactpage():
    return template("contact.html")
