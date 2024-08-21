from flask import Flask, render_template, abort, request
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
    # get planting instructions information
    cursor.execute("SELECT * FROM Planting_instruction WHERE id=?;", (id,))
    instruction = cursor.fetchone()
    cursor.execute("SELECT * FROM Plant WHERE id=?;", (id,))
    plant = cursor.fetchone()
    cursor.execute("SELECT * FROM PlantRegion WHERE regionid=?;", (id,))
    plantregion = cursor.fetchone()
    cursor.execute("SELECT * FROM Regionlist WHERE id=?;", (id,))
    regionlist = cursor.fetchall()
    if not id:
        abort(404)
    # else return plant page
    else:
        return render_template('plant.html', plant=plant,
                               planting_instruction=instruction,
                               plantregion=plantregion,
                               regionlist=regionlist)


@app.route('/search', methods=['GET', 'POST'])
def search():
    search_term = request.args.get('search_term', '')
    connect = sqlite3.connect('plant.db')
    cursor = connect.cursor()
    # get search from Plant table
    result = cursor.execute("SELECT * FROM Plant WHERE name LIKE ?;",
                            (f"%{search_term}%", )).fetchall()
    connect.close()
    return render_template("search.html", result=result,
                           search_term=search_term)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


# about/contact information page
@app.route('/contact')
def contactpage():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
