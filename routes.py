from flask import Flask, render_template
import sqlite3

app = Flask(__name__)


# homepage
@app.route('/')
def homepage():
    return render_template("home.html")


# all plants page
@app.route('/all_plant')
def all_plant():
    connect = sqlite3.connect('plant.db')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM Plant ORDER BY id;")
    plants = cursor.fetchall()
    connect.close()
    return render_template('all_plant.html', plant=plants)


# individual plants page
@app.route('/plant/<int:id>')
def plant(id):
    connect = sqlite3.connect('plant.db')
    cursor = connect.cursor()
    cursor.execute("SELECT * FROM Plant WHERE id=?", (id,))
    plant = cursor.fetchone()
    # planting instruction
    cursor.execute("SELECT * FROM Planting_instruction WHERE id=?;", (id,))
    instruction = cursor.fetchone()
    connect.close()
    if '<int:id' == 'NULL':
        return render_template('404.html')
    else:
        return render_template('plant.html', plant=plant,
                               planting_instruction=instruction)


# about/contact information page
@app.route('/contact')
def contactpage():
    return render_template("contact.html")


'''
# triangles
@app.route('/triangle/<int:size>')
def triangle_pattern(size):
    triangle = ""
    for i in range(size):
        triangle += (i+1)*'*' + "<br>"
    return (triangle)
'''


if __name__ == "__main__":
    app.run(debug=True)
