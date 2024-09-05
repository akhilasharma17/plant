from flask import Flask, render_template, abort, request, redirect
import sqlite3

app = Flask(__name__)


# homepage
@app.route('/')
def homepage():
    return render_template("home.html")


# all plants page
@app.route('/all_plant')
def all_plant():
    conn = sqlite3.connect('plant.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Plant ORDER BY id;")
    plants = cursor.fetchall()
    conn.close()
    return render_template('all_plant.html', plant=plants)


# individual plants page
@app.route('/plant/<int:id>')
def plant(id):
    conn = sqlite3.connect('plant.db')
    cursor = conn.cursor()
    # get planting instructions information
    cursor.execute("SELECT * FROM Planting_instruction WHERE id=?;", (id,))
    instruction = cursor.fetchone()
    cursor.execute("SELECT * FROM Plant WHERE id=?;", (id,))
    plant = cursor.fetchone()
    # figure out foreign key here
    cursor.execute("SELECT * FROM PlantRegion WHERE regionid=?;", (id,))
    plantregion = cursor.fetchone()
    cursor.execute("SELECT * FROM Regionlist WHERE id=?;", (id,))
    regionlist = cursor.fetchall()
    conn.close()
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
    status = request.args.get('status', '')
    conn = sqlite3.connect('plant.db')
    cursor = conn.cursor()
    # get search from Plant table
    result = cursor.execute("SELECT * FROM Plant WHERE name LIKE ?;",
                            (f"%{search_term}%", )).fetchall()
    # status filter
    status = cursor.execute
    ("SELECT * FROM Plant WHERE name LIKE ? AND status = ?")
    conn.close()
    return render_template("search.html", result=result,
                           search_term=search_term, status=status)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


# about/contact information page
@app.route('/contact')
def contactpage():
    return render_template("contact.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('plant.db')
        cursor = conn.cursor()
        user = cursor.execute('SELECT * FROM users WHERE username = ?',
                              (username,)).fetchone()
        conn.close()  # Ensure the connection is closed

        if user and user['password'] == password:
            return redirect('/')
        else:
            message = 'Invalid credentials, please try again.'

    return render_template('login.html', message=message)


if __name__ == "__main__":
    app.run(debug=True)
