#Create App.py using Flask for a Web Interface
import sqlite3
import datetime
from flask import Flask, render_template, request, redirect, url_for, g # Import 'g'

app = Flask(__name__)

"""
goals = [] #Use a database later

#Creating a home page for all the goals and its status
@app.route('/')
def index():
    current_date = datetime.date.today()
    for goal in goals:
        goal['status'] = "Upcoming"
        if goal['deadline'] < current_date:
            goal['status'] = "Past Due"
        elif goal['deadline'] == current_date:
            goal['status'] = "Due Today"
    return render_template('index.html', goals=goals)
"""

#Implementing a SQLITE3 Database to store goals

DATABASE = 'goals.db'

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row # Allows accessing columns by name
    return g.db

def close_db():
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')

@app.teardown_appcontext
def teardown_db(error):
    close_db()



#Creating a home page for all the goals and its status
"""
@app.route('/')
def index():
    current_date = datetime.date.today()
    for goal in goals:
        goal['status'] = "Upcoming"
        if goal['deadline'] < current_date:
            goal['status'] = "Past Due"
        elif goal['deadline'] == current_date:
            goal['status'] = "Due Today"
    return render_template('index.html', goals=goals)
"""
@app.route('/add', methods=["GET", "POST"])
def add_goal():
    if request.method == "POST":
        description = request.form['description']
        deadline_str = request.form['deadline']
        db = get_db()
        try:
            deadline = datetime.datetime.strptime(deadline_str, "%Y-%m-%d").date() # Assuming your HTML form uses YYYY-MM-DD
            db.execute('INSERT INTO goals (description, deadline) VALUES (?, ?)',
                       (description, deadline.strftime('%Y-%m-%d')))
            db.commit()
            return redirect(url_for('index'))
        except ValueError:
            return "Invalid date format"
        finally:
            close_db() # Explicitly close the connection for now, though teardown will also handle it
    return render_template('add.html')

"""
@app.route('/add', methods=["GET", "POST"])
def add_goal():
    if request.method == "POST":
        description = request.form['description']
        deadline_str = request.form['deadline']

        try:
            deadline = datetime.datetime.strptime(deadline_str, "%Y-%m-%d").date() # Adjust format as needed
            goals.append({'description': description, 'deadline': deadline})
            return redirect(url_for('index'))
        except ValueError:
            return "Invalid date format" # Better error handling needed

    return render_template('add.html')
"""
@app.route('/')
def index():
    conn = get_db()
    goals_db = conn.execute('SELECT id, description, deadline FROM goals').fetchall()
    completed_goals_db = conn.execute('SELECT id, description, deadline, completion_date FROM goals_completed').fetchall()
    conn.close()
    active_goals = []
    current_date = datetime.date.today()
    for row in goals_db:
        deadline_str = row['deadline']
        deadline = datetime.datetime.strptime(deadline_str, '%Y-%m-%d').date()
        status = "Upcoming"
        if deadline < current_date:
            status = "Past Due"
        elif deadline == current_date:
            status = "Due Today"
        active_goals.append({'id': row['id'], 'description': row['description'], 'deadline': deadline, 'status': status})
    completed_goals = []
    if completed_goals_db: # Check if there are any completed goals
        for row in completed_goals_db:
            completed_goals.append({'id': row['id'], 'description': row['description'], 'deadline': row['deadline'], 'completion_date': row['completion_date']})

    return render_template('index.html', active_goals=active_goals, completed_goals=completed_goals)



@app.route('/complete/<int:goal_id>', methods=['POST'])
def complete_goal(goal_id):
    db = get_db()
    try:
        # Fetch the goal details from the active goals table
        goal = db.execute('SELECT description, deadline FROM goals WHERE id = ?', (goal_id,)).fetchone()

        if goal:
            # Insert the goal into the completed goals table with the completion date
            completion_date = datetime.date.today().strftime('%Y-%m-%d')
            db.execute('INSERT INTO goals_completed (description, deadline, completion_date) VALUES (?, ?, ?)',
                       (goal['description'], goal['deadline'], completion_date))

            # Delete the goal from the active goals table
            db.execute('DELETE FROM goals WHERE id = ?', (goal_id,))
            db.commit()
        else:
            # Handle the case where the goal ID might not exist (optional)
            print(f"Goal with ID {goal_id} not found.")

    except sqlite3.Error as e:
        print(f"Database error: {e}")
        db.rollback() # Rollback changes in case of an error
    finally:
        close_db()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
