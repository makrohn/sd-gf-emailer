"""
A program to find recently-closed JIRA tickets and email
a google form to request feedback.
"""

import json
import requests
import smtplib
from email.mime.text import MIMEText
import settings


def getIssuesFromToday():
    """Fetch a JSON file of issues according to filter"""
    r = requests.get(
        settings.api_base_url + "/search?jql=" + settings.search_filter +
        "&fields=" + settings.fields,
        auth=(
            settings.username,
            settings.password
            )
        )
    return r.json()


def sendSurvey(issue):
    """Send a an email to the reporter of an issue"""
    msg = MIMEText(
        'Hello!\n\n The Help Desk has recently closed your ticket, "' +
        issue['fields']['summary'] + '". If you have a moment, please fill out ' +
        ' this survey on how happy you are with your Help Desk experience.\n\n' +
        settings.google_form_link + '?entry.' +
        'settings.ticket_number_field' + '=' +
        issue['key'] + '\n\nThanks!\nThe Help Desk Staff'
        )
    msg['Subject'] = "Help Desk Survey for Ticket " + issue['key']
    msg['From'] = settings.from_address
    msg['To'] = issue['fields']['reporter']['emailAddress']
    s = smtplib.SMTP(settings.smtp_server)
    s.sendmail(
        settings.from_address,
        [issue['fields']['reporter']['emailAddress']],
        msg.as_string()
        )
    print msg


def addLabel(issue_key):
    """Add a label indicating that a survey has been sent to the requestor"""
    json_data = json.dumps({"update": {"labels": [{"add": "survey_sent"}]}})
    headers = {'Content-Type': 'application/json', }
    r = requests.put(
        url=settings.api_base_url + '/issue/' + issue_key,
        data=json_data,
        auth=(
            settings.username,
            settings.password
            ),
        headers=headers
        )
    print r.status_code
    print r.text

todaysIssues = getIssuesFromToday()

for ticket in todaysIssues['issues']:
    if 'survey_sent' not in ticket['fields']['labels']:
        sendSurvey(ticket)
        addLabel(ticket['key'])
