from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


# homepage
@app.route('/')
def homepage():
    return render_template("home.html")


'''
# all plants page
@app.route('/plant/all_plant')
def all_plant():
    connect = sqlite3.connect('plant.db')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM Plant ORDER BY id", (id,))
    all_plant = cursor.fetchall()
    return render_template('plant.html', plant=all_plant)
'''


# individual plants page
@app.route('/plant/<int:id>')
def plant(id):
    connect = sqlite3.connect('plant.db')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM Plant WHERE id=?", (id,))
    plant = cursor.fetchone()
    return render_template('plant.html', plant=plant)


# about/contact information page
@app.route('/contact')
def contactpage():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
