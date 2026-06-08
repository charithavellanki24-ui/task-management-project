from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "tasksecret"

def init_db():
    conn = sqlite3.connect("tasks.db")
    c = conn.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    ''')

    c.execute('''
    CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        status TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()

        try:
            c.execute(
                "INSERT INTO users(username,password) VALUES(?,?)",
                (username,password)
            )
            conn.commit()
            return redirect('/login')
        except:
            return "Username already exists"

    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('tasks.db')
        c = conn.cursor()

        c.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username,password)
        )

        user = c.fetchone()

        if user:
            session['user_id'] = user[0]
            return redirect('/dashboard')

        return "Invalid Login"

    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()

    c.execute(
        "SELECT * FROM tasks WHERE user_id=?",
        (session['user_id'],)
    )

    tasks = c.fetchall()

    return render_template('dashboard.html', tasks=tasks)

@app.route('/add', methods=['POST'])
def add_task():
    title = request.form['title']

    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()

    c.execute(
        "INSERT INTO tasks(user_id,title,status) VALUES(?,?,?)",
        (session['user_id'], title, "Pending")
    )

    conn.commit()
    return redirect('/dashboard')

@app.route('/complete/<int:id>')
def complete(id):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()

    c.execute(
        "UPDATE tasks SET status='Completed' WHERE id=?",
        (id,)
    )

    conn.commit()
    return redirect('/dashboard')

@app.route('/delete/<int:id>')
def delete(id):
    conn = sqlite3.connect('tasks.db')
    c = conn.cursor()

    c.execute("DELETE FROM tasks WHERE id=?", (id,))
    conn.commit()

    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == "__main__":
    app.run(debug=True)