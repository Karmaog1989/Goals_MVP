# Create App.py using Flask for a Web Interface
import sqlite3  # Imports the SQLite library for database interaction
import datetime  # Imports the datetime module for working with dates and times
from flask import Flask, render_template, request, redirect, url_for, g  # Imports necessary modules from the Flask framework

app = Flask(__name__)  # Creates an instance of the Flask application

# Implementing a SQLITE3 Database to store goals

DATABASE = 'goals.db'  # Defines the name of the SQLite database file

def get_db():  # Defines a function to get the database connection
    if 'db' not in g:  # Checks if a database connection is already stored in the Flask 'g' object
        g.db = sqlite3.connect(DATABASE)  # If not, establishes a new connection to the database
        g.db.row_factory = sqlite3.Row  # Configures the connection to return rows as dictionary-like objects
    return g.db  # Returns the database connection

def close_db():  # Defines a function to close the database connection
    db = g.pop('db', None)  # Removes the database connection from the 'g' object
    if db is not None:  # Checks if a database connection exists
        db.close()  # Closes the database connection

def init_db():  # Defines a function to initialize the database from the schema file
    with app.app_context():  # Creates an application context for database operations
        db = get_db()  # Gets the database connection
        with app.open_resource('schema.sql', mode='r') as f:  # Opens the 'schema.sql' file in read mode
            db.cursor().executescript(f.read())  # Executes the SQL commands from the schema file
        db.commit()  # Saves the changes to the database

@app.cli.command('initdb')  # Registers a command 'initdb' that can be run from the command line
def initdb_command():  # Defines the function that will be executed when the 'initdb' command is run
    """Initializes the database."""
    init_db()  # Calls the init_db function to initialize the database
    print('Initialized the database.')  # Prints a message to the console

@app.teardown_appcontext  # Registers a function to be called after each request, even if there's an error
def teardown_db(error):  # Defines the function to close the database connection at the end of a request
    close_db()  # Calls the close_db function to close the database connection


@app.route('/')  # Defines the route for the homepage ('/')
def index():  # Defines the function that handles requests to the homepage
    conn = get_db()  # Gets the database connection
    goals_db = conn.execute('SELECT id, description, deadline FROM goals').fetchall()  # Executes an SQL SELECT statement to fetch all goals
    completed_goals_db = conn.execute('SELECT id, description, deadline, completion_date FROM goals_completed').fetchall()  # Executes an SQL SELECT statement to fetch all completed goals
    conn.close()  # Closes the database connection
    active_goals = []  # Initializes an empty list to store active goals
    current_date = datetime.date.today()  # Gets the current date
    for row in goals_db:  # Iterates through each goal fetched from the database
        deadline_str = row['deadline']  # Gets the deadline string from the row
        deadline = datetime.datetime.strptime(deadline_str, '%Y-%m-%d').date()  # Converts the deadline string to a date object
        status = "Upcoming"  # Sets the initial status to "Upcoming"
        if deadline < current_date:  # Checks if the deadline is in the past
            status = "Past Due"  # Updates the status to "Past Due"
        elif deadline == current_date:  # Checks if the deadline is today
            status = "Due Today"  # Updates the status to "Due Today"
        active_goals.append({'id': row['id'], 'description': row['description'], 'deadline': deadline, 'status': status})  # Appends a dictionary representing the goal to the active_goals list
    completed_goals = []  # Initializes an empty list to store completed goals
    if completed_goals_db:  # Checks if there are any completed goals
        for row in completed_goals_db:  # Iterates through each completed goal
            completed_goals.append({'id': row['id'], 'description': row['description'], 'deadline': row['deadline'], 'completion_date': row['completion_date']})  # Appends a dictionary representing the completed goal to the completed_goals list

    return render_template('index.html', active_goals=active_goals, completed_goals=completed_goals)  # Renders the 'index.html' template, passing the active_goals and completed_goals lists


@app.route('/add', methods=["GET", "POST"])  # Defines a route for adding goals, accepting both GET and POST requests
def add_goal():  # Defines the function that handles requests to the '/add' route
    if request.method == "POST":  # Checks if the request method is POST (form submission)
        description = request.form['description']  # Retrieves the goal description from the submitted form data
        deadline_str = request.form['deadline']  # Retrieves the goal deadline from the submitted form data
        db = get_db()  # Gets the database connection
        try:
            deadline = datetime.datetime.strptime(deadline_str, "%Y-%m-%d").date()  # Converts the deadline string to a date object
            db.execute('INSERT INTO goals (description, deadline) VALUES (?, ?)',  # Executes an SQL INSERT statement to add a new goal
                     (description, deadline.strftime('%Y-%m-%d')))  # Provides the values for the description and deadline
            db.commit()  # Saves the changes to the database
            return redirect(url_for('index'))  # Redirects the user to the homepage ('index' route)
        except ValueError:  # Catches an error if the date format is invalid
            return "Invalid date format"  # Returns an error message to the user
        finally:
            close_db()  # Explicitly closes the database connection
    return render_template('add.html')  # Renders the 'add.html' template for GET requests (displaying the form)



@app.route('/complete/<int:goal_id>', methods=['POST'])  # Defines a route for completing a goal, accepting only POST requests
def complete_goal(goal_id):  # Defines the function that handles requests to the '/complete/<goal_id>' route
    db = get_db()  # Gets the database connection
    try:
        # Fetch the goal details from the active goals table
        goal = db.execute('SELECT description, deadline FROM goals WHERE id = ?', (goal_id,)).fetchone()  # Executes an SQL SELECT statement to fetch the goal by its ID

        if goal:  # Checks if the goal was found
            # Insert the goal into the completed goals table with the completion date
            completion_date = datetime.date.today().strftime('%Y-%m-%d')  # Gets the current date as a string for the completion date
            db.execute('INSERT INTO goals_completed (description, deadline, completion_date) VALUES (?, ?, ?)',  # Executes an SQL INSERT statement to add the goal to the completed table
                     (goal['description'], goal['deadline'], completion_date))  # Provides the goal details and completion date

            # Delete the goal from the active goals table
            db.execute('DELETE FROM goals WHERE id = ?', (goal_id,))  # Executes an SQL DELETE statement to remove the goal from the active goals table
            db.commit()  # Saves the changes to the database
        else:
            # Handle the case where the goal ID might not exist (optional)
            print(f"Goal with ID {goal_id} not found.")  # Prints a message if the goal ID is not found

    except sqlite3.Error as e:  # Catches any SQLite database errors
        print(f"Database error: {e}")  # Prints the error message
        db.rollback()  # Rolls back any pending changes in case of an error
    finally:
        close_db()  # Closes the database connection
    return redirect(url_for('index'))  # Redirects the user to the homepage

if __name__ == '__main__':  # Checks if the script is being run directly
    app.run(host='0.0.0.0', debug=True)  # Starts the Flask development server
