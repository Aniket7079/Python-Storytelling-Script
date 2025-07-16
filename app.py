
from flask import Flask, render_template, request, redirect, url_for, flash
from dotenv import load_dotenv
load_dotenv()
from report_generator import generate_report, create_issue_in_jira, search_issues_from_jira

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

@app.route('/')
def home():
    return redirect(url_for('create_issue'))

@app.route('/create-issue', methods=['GET', 'POST'])
def create_issue():
    if request.method == 'POST':
        summary = request.form['summary']
        description = request.form['description']
        issue_type = request.form['issue_type']

        created = create_issue_in_jira(summary, description, issue_type)
        if created:
            flash('Issue created successfully!', 'success')
        else:
            flash('Failed to create issue.', 'danger')
        
        # After creation, generate and show report
        report = generate_report()
        return render_template('report.html', report=report)

    return render_template('create_issue.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        query = request.form['query']
        results = search_issues_from_jira(query)
    return render_template('search.html', results=results)

@app.route('/report')
def report():
    report = generate_report()
    return render_template('report.html', report=report)

if __name__ == '__main__':
    app.run(debug=True)
