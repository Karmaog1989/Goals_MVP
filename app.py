#Create App.py using Flask for a Web Interface

from flask import Flask, render_template, request, redirect, url_for
import datetime

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
