from flask import Flask, request, redirect, render_template
import sqlite3
import string
import random
app = Flask(__name__)

DATABASE = 'urls.db'

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                original_url TEXT NOT NULL,
                short_url TEXT NOT NULL UNIQUE,
                clicks INTEGER DEFAULT 0
            )
        ''')
        db.commit()

init_db()

def generate_short_link(length=6):
    characters = string.ascii_letters + string.digits
    short_link = ''.join(random.choice(characters) for _ in range(length))
    return short_link

@app.route('/', methods=['GET', 'POST'])
def index():
    short_url = None
    if request.method == 'POST':
        original_url = request.form['original_url']
        short_url = generate_short_link()

        db = get_db()
        cursor = db.cursor()
        cursor.execute('INSERT INTO urls (original_url, short_url) VALUES (?, ?)', (original_url, short_url))
        db.commit()
        short_url = request.host_url + short_url

    return render_template('index.html', short_url=short_url)

@app.route('/<short_url>')
def redirect_to_url(short_url):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT original_url, clicks FROM urls WHERE short_url = ?', (short_url,))
    result = cursor.fetchone()
    if result:
        original_url, clicks = result
        cursor.execute('UPDATE urls SET clicks = ? WHERE short_url = ?', (clicks + 1, short_url))
        db.commit()
        return redirect(original_url)
    return 'URL not found', 404

if __name__ == '__main__':
    app.run(debug=True)
