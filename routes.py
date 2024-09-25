from flask import Flask, render_template, abort
from flask import request, redirect, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import secrets


app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex(24)


# homepage and watchlist
@app.route('/')
def homepage():
    # get the username from the session so that we can get the watched plants
    username = session.get('username')
    if username:
        params = []
        query = """
            SELECT plant.* FROM Plant
            JOIN Watchlist ON Plant.id = Watchlist.plant_id
            JOIN User ON User.id = Watchlist.user_id
            WHERE User.username = ?;
            """
        params.append(username)
        plant = db_query(query, False, params)
    else:
        plant = []
    return render_template("home.html", plant=plant, username=username)


@app.route('/add_to_watchlist/<int:plant_id>', methods=['POST'])
def add_to_watchlist(plant_id):
    username = session.get('username')
    # session['_flashes'] = []
    if not username:
        flash("You need to log in to add plants to your watchlist")
        return redirect('/login')
    user_query = "SELECT id FROM User WHERE username = ?;"
    user = db_query(user_query, single=True, params=(username,))
    if user:
        user_id = user[0]
        check_query = """SELECT * FROM Watchlist
        WHERE user_id = ? AND plant_id = ?;"""
        existing = db_query(check_query, single=True,
                            params=(user_id, plant_id))
        if existing:
            flash("This plant is already in your watchlist.", "info")
        else:
            insert_query = """
                            INSERT INTO Watchlist(user_id, plant_id)
                            VALUES (?, ?);"""
            db_insert(insert_query, params=(user_id, plant_id))
            flash("Plant added to your watchlist.", "success")
    else:
        flash("User not found.", "error")
    return redirect(f'/plant/{plant_id}')


@app.route('/remove_watchlist/<int:plant_id>', methods=['POST'])
def remove_watchlist(plant_id):
    # Get the username from the session
    username = session.get('username')
    if not username:
        flash('You need to be logged in to remove plants from your watchlist.',
              'error')
        return redirect('/login')
    # get the user id
    user_query = "SELECT id FROM User WHERE username = ?"
    user = db_query(user_query, single=True, params=(username,))
    if not user:
        flash('User not found.', 'error')
        return redirect('/')
    user_id = user[0]
    # remove the plant from the user's watchlist
    remove_query = "DELETE FROM Watchlist WHERE user_id = ? AND plant_id = ?"
    db_insert(remove_query, params=(user_id, plant_id))
    flash('Plant removed from your watchlist.', 'success')
    return redirect('/')


# function with connection to query database and to avoid redundant code
def db_query(query, single=False, params=()):
    conn = sqlite3.connect('plant.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    # if single=True, fetch only one result, or else fetch all
    if single:
        result = cursor.fetchone()
    else:
        result = cursor.fetchall()
    conn.close()
    return result


# function with connection to insert into database
def db_insert(query, params=()):
    conn = sqlite3.connect('plant.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    conn.commit()
    conn.close()


# all plants page
@app.route('/all_plant', methods=['GET'])
def all_plant():
    status_filter = request.args.get('status', '').strip()
    query = "SELECT * FROM Plant"
    params = []
    # add the status selected to the query to filter
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
    # query for plant region using JOIN to get region names
    plant_region_query = """
                        SELECT Region.name FROM Region
                        JOIN PlantRegion ON Region.id = PlantRegion.region_id
                        WHERE PlantRegion.plant_id = ?;
                        """
    plant_region = db_query(plant_region_query, single=False, params=(id,))
    plant_query = "SELECT * FROM Plant WHERE id=?;"
    plant = db_query(plant_query, single=True, params=(id,))
    username = session.get('username')
    # check if the id is incorrect so that we can show the 404
    if not plant:
        abort(404)
    else:
        return render_template('plant.html',
                               planting_instruction=instruction,
                               plant=plant,
                               plant_region=plant_region,
                               username=username)


@app.route('/search', methods=['GET'])
def search():
    search_term = request.args.get('search_term', '').strip()
    # get search from Plant table BECAUSE
    query = "SELECT * FROM Plant WHERE name LIKE ?;"
    result = db_query(query, single=False,
                      params=(f"%{search_term}%",))
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
        user_query = "SELECT * FROM User where username = ?"
        existing_user = db_query(user_query, single=True, params=(username,))
        # check if the user already exists so we don't get repeat usernames
        if existing_user:
            flash('Username already exists. Please choose another one.',
                  "error")
            return redirect('/signup')
        # hash the password for extra security
        hashed_password = generate_password_hash(password)
        insert_query = "INSERT INTO User (username, password) VALUES (?, ?)"
        db_insert(insert_query, params=(username, hashed_password))
        flash("Your account has been created. Please log in.", "success")
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
        if user and check_password_hash(user[2], password):
            session['username'] = username
            flash("Login successful.", "success")
            return redirect('/')
        else:
            message = 'Invalid credentials. Please try again.'
    return render_template('login.html', message=message)


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash("You have been logged out.", "success")
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
