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
    # planting instruction
    cursor.execute("SELECT * FROM Planting_instruction WHERE id=?", (id,))
    instruction = cursor.fetchone()
    return render_template('plant.html', plant=plant,
                           planting_instruction=instruction)


# about/contact information page
@app.route('/contact')
def contactpage():
    return render_template("contact.html")


# triangles
@app.route('/triangle/<int:size>')
def triangle_pattern(size):
    triangle = ""
    for i in range(size):
        triangle += (i+1)*'*' + "<br>"
    return (triangle)


if __name__ == "__main__":
    app.run(debug=True)
