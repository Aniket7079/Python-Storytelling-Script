# report_generator.py

import requests
import matplotlib.pyplot as plt
import os
from config import JIRA_SITE, JIRA_EMAIL, JIRA_API_TOKEN, PROJECT_KEY

def generate_report():
    url = f"{JIRA_SITE}/rest/api/3/search"
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)
    headers = {"Accept": "application/json"}
    params = {"jql": f"project={PROJECT_KEY}", "maxResults": 100}

    response = requests.get(url, headers=headers, auth=auth, params=params)
    issues = response.json().get("issues", [])

    total_issues = len(issues)
    done_issues = 0
    pending_issues = 0

    status_counts = {}
    priority_counts = {}

    for issue in issues:
        fields = issue["fields"]
        status = fields["status"]["name"]
        priority = fields.get("priority", {}).get("name", "None")

        # Categorize tasks
        if status.lower() in ["done", "closed", "resolved"]:
            done_issues += 1
        else:
            pending_issues += 1

        # Count status
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1

        # Count priority
        if priority not in priority_counts:
            priority_counts[priority] = 0
        priority_counts[priority] += 1

    # Generate summary report
    report_text = f"""
Total Issues: {total_issues}
✅ Done Tasks: {done_issues}
⏳ Pending Tasks: {pending_issues}
"""

    # Create charts directory
    os.makedirs("static", exist_ok=True)

    # Status chart
    status_labels = list(status_counts.keys())
    status_values = list(status_counts.values())

    plt.figure(figsize=(6, 4))
    plt.bar(status_labels, status_values, color='mediumseagreen')
    plt.title("Issue Status Distribution")
    plt.xlabel("Status")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    status_chart_path = "static/status_chart.png"
    plt.tight_layout()
    plt.savefig(status_chart_path)
    plt.close()

    # Priority pie chart
    priority_labels = list(priority_counts.keys())
    priority_values = list(priority_counts.values())

    plt.figure(figsize=(6, 6))
    plt.pie(priority_values, labels=priority_labels, autopct="%1.1f%%", startangle=90)
    plt.title("Issue Priority Distribution")
    priority_chart_path = "static/priority_chart.png"
    plt.tight_layout()
    plt.savefig(priority_chart_path)
    plt.close()

    return report_text, [status_chart_path, priority_chart_path]
