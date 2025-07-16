import os
import datetime
import matplotlib.pyplot as plt
from jira import JIRA
from collections import defaultdict
from dotenv import load_dotenv
load_dotenv()


JIRA_SERVER = os.getenv('JIRA_SERVER')
JIRA_USER = os.getenv('JIRA_USER')
JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN')
PROJECT_KEY = os.getenv('PROJECT_KEY')

def connect_to_jira():
    return JIRA(server=JIRA_SERVER, basic_auth=(JIRA_USER, JIRA_API_TOKEN))

def fetch_issues(jira_client):
    return jira_client.search_issues(f'project = {PROJECT_KEY}', maxResults=100)

def analyze_issues(issues):
    analysis = {
        'count': len(issues),
        'by_status': defaultdict(int),
        'by_priority': defaultdict(int),
        'by_type': defaultdict(int),
    }
    for issue in issues:
        analysis['by_status'][issue.fields.status.name] += 1
        analysis['by_priority'][getattr(issue.fields.priority, 'name', 'Unprioritized')] += 1
        analysis['by_type'][issue.fields.issuetype.name] += 1
    return analysis

def visualize_data(analysis):
    charts = []
    # Status Pie
    plt.figure()
    plt.pie(analysis['by_status'].values(), labels=analysis['by_status'].keys(), autopct='%1.1f%%')
    plt.title('Status Distribution')
    filename1 = 'static/status_chart.png'
    plt.savefig(filename1)
    plt.close()
    charts.append(filename1)

    # Priority Bar
    plt.figure()
    plt.bar(analysis['by_priority'].keys(), analysis['by_priority'].values(), color='skyblue')
    plt.title('Priority Distribution')
    filename2 = 'static/priority_chart.png'
    plt.savefig(filename2)
    plt.close()
    charts.append(filename2)

    return charts

def generate_report():
    jira = connect_to_jira()
    issues = fetch_issues(jira)
    analysis = analyze_issues(issues)
    charts = visualize_data(analysis)
    report = f"Total Issues: {analysis['count']}\n"
    return report, charts

def create_issue_in_jira(summary, description, issue_type):
    try:
        jira = connect_to_jira()
        new_issue = jira.create_issue(
            project=PROJECT_KEY,
            summary=summary,
            description=description,
            issuetype={'name': issue_type}
        )
        return new_issue is not None
    except Exception as e:
        print(f"Error: {e}")
        return False

def search_issues_from_jira(query):
    try:
        jira = connect_to_jira()
        jql = f'text ~ "{query}" ORDER BY updated DESC'
        issues = jira.search_issues(jql, maxResults=10)
        return issues
    except Exception as e:
        print(f"Search error: {e}")
        return []
