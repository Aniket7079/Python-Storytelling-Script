from flask import Flask, render_template, request, redirect, session, flash, url_for
import sqlite3
import smtplib, ssl
from email.message import EmailMessage
import requests
from collections import Counter
from report_generator import generate_report
import os

app = Flask(__name__)
app.secret_key = 'supersecret123'

# JIRA CONFIG
JIRA_URL = 'https://clouddaystech.atlassian.net'
JIRA_API_TOKEN = 'ATATT3xFfGF081iJdTvTSVaaf3snc5umh302y2z62AA2FiBdvuETEZoxqA7u1sDUTeV06YMIKXi8oa9zsPBZhSYGOoUui-WDj7L6bA9SgiCEGhBx1sTkYclL5s0dsNEjtORPFv-p-bkz4I0N-tF_f2xk4zjoH_7Adz5st0HoNw4194SU_oOBPog=8906A4AC'
JIRA_USER_EMAIL = 'aniket.thale@clouddaystech.com'
JIRA_PROJECT_KEY = 'PSS'

# EMAIL CONFIG
EMAIL_SENDER = 'aniketthale02019@gmail.com'
EMAIL_PASSWORD = 'glzd zzgu rykp jxbf'

# DATABASE INIT
def init_db():
    with sqlite3.connect('users.db') as con:
        cur = con.cursor()
        cur.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )''')
        con.commit()



# USER ROUTES
@app.route('/')
def home():
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        con = sqlite3.connect('users.db')
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cur.fetchone()
        con.close()
        if user:
            session['user'] = user[1]
            flash("Welcome back!", "success")
            return redirect('/dashboard')
        else:
            flash("Invalid credentials", "danger")
            return redirect('/login')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        try:
            con = sqlite3.connect('users.db')
            cur = con.cursor()
            cur.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
            con.commit()
            con.close()
            flash("Account created! Please login.", "success")
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash("Email already registered.", "danger")
            return redirect('/signup')
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash("Logged out successfully.", "info")
    return redirect('/login')

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

# ISSUE CREATION
@app.route('/create_issue', methods=['POST'])
def create_issue():
    if 'user' not in session:
        return redirect('/login')
    summary = request.form['summary']
    description = request.form['description']
    issuetype = request.form['issuetype']
    
    # JIRA API Call
    url = f"{JIRA_URL}/rest/api/2/issue"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    auth = (JIRA_USER_EMAIL, JIRA_API_TOKEN)
    payload = {
        "fields": {
            "project": {"key": JIRA_PROJECT_KEY},
            "summary": summary,
            "description": description,
            "issuetype": {"name": issuetype}
        }
    }

    response = requests.post(url, auth=auth, json=payload, headers=headers)

    if response.status_code == 201:
        send_email(summary, issuetype)
        flash(f"Issue '{summary}' created successfully.", "success")
    else:
        flash("Failed to create issue. Check JIRA credentials.", "danger")
    return redirect('/dashboard')

# EMAIL NOTIFICATION FUNCTION
def send_email(summary, issuetype):
    msg = EmailMessage()
    msg.set_content(f"A new issue has been created in JIRA.\n\nSummary: {summary}\nType: {issuetype}")
    msg['Subject'] = f"🛠️ New JIRA Issue: {summary}"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_SENDER

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

# SEARCH ISSUES
@app.route('/search')
def search():
    query = request.args.get('query', '')
    if not query:
        return redirect('/dashboard')

    # You can enhance this by querying JIRA with JQL
    search_results = [f"Issue matching: {query}"]  # Placeholder
    return render_template("dashboard.html", search_results=search_results)

# REPORT WITH PIE CHART
@app.route('/report')
def report():
    # Example static data - in real project fetch from JIRA API
    issues = ["Bug", "Bug", "Task", "Story", "Task", "Task"]
    count = Counter(issues)
    labels = list(count.keys())
    data = list(count.values())
    report_text, *_ = generate_report()
    return render_template("report.html", labels=labels, data=data, report_text=report_text)

# RUN
if __name__ == '__main__':
    app.run(debug=True) 
