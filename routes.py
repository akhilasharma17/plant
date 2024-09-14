from flask import Flask, render_template, abort, request, redirect, flash
import sqlite3
# from werkzeug.security import generate_password_hash


app = Flask(__name__)
app.secret_key = 'your_secret_key'


# homepage
@app.route('/')
def homepage():
    return render_template("home.html")


def db_query(query, single=False, params=()):
    conn = sqlite3.connect('plant.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    if single:
        result = cursor.fetchone()
    else:
        result = cursor.fetchall()
    conn.close()
    return result


# all plants page
@app.route('/all_plant', methods=['GET'])
def all_plant():
    status_filter = request.args.get('status', '').strip()
    query = "SELECT * FROM Plant"
    params = []
    # add the status selected to the query
    if status_filter:
        query += " WHERE status = ?"
        params.append(status_filter)
    plants = db_query(query, single=False, params=params)
    return render_template('all_plant.html',
                           plant=plants,
                           status_filter=status_filter)


# individual plants page
@app.route('/plant/<int:id>')
def plant(id):
    instruction_query = "SELECT * FROM Planting_instruction WHERE id=?;"
    instruction = db_query(instruction_query, single=True, params=(id,))
    plant_region_query = "SELECT * FROM PlantRegion WHERE regionid=?;"
    plant_region = db_query(plant_region_query, single=True, params=(id,))
    region_list_query = "SELECT * FROM Regionlist WHERE id=?;"
    region_list = db_query(region_list_query, single=False, params=(id,))
    plant_query = "SELECT * FROM Plant WHERE id=?;"
    plant = db_query(plant_query, single=True, params=(id,))
    if not plant:
        abort(404)
    # else return plant page
    else:
        return render_template('plant.html',
                               planting_instruction=instruction,
                               plant=plant,
                               plantregion=plant_region,
                               regionlist=region_list)


@app.route('/search', methods=['GET'])
def search():
    search_term = request.args.get('search_term', '').strip()
    # get search from Plant table BECAUSE
    query = "SELECT * FROM Plant WHERE name LIKE ?;"
    result = db_query(query, single=False, params=(f"%{search_term}%",))
    return render_template("search.html",
                           result=result,
                           search_term=search_term)


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


# about/contact information page
@app.route('/contact')
def contactpage():
    return render_template("contact.html")


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        query = 'INSERT INTO User (username, password) VALUES (?, ?)'
        db_query(query, single=False, params=(username, password))
        flash('Your account has been created. Please log in.')
        return redirect('/login')
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        query = 'SELECT * FROM User WHERE username = ?'
        user = db_query(query, single=True, params=(username,))
        if user and user[2] == password:
            return redirect('/')
        else:
            message = 'Invalid credentials, please try again.'
    return render_template('login.html', message=message)


if __name__ == "__main__":
    app.run(debug=True)
