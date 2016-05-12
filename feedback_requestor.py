#Copyright 2015 Matthew Krohn
#
#This program is free software: you can redistribute it and/or modify
#it under the terms of the GNU General Public License as published by
#the Free Software Foundation, either version 3 of the License, or
#(at your option) any later version.
#
#This program is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#GNU General Public License for more details.
#
#You should have received a copy of the GNU General Public License
#along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
A program to find recently-closed JIRA tickets and email
a google form to request feedback.
"""

import json
import smtplib
from email.mime.text import MIMEText
import re
import requests
from validate_email import validate_email
import settings


def sanitize(string):
    """Remove unwanted or dangerous character from a string"""
    new_string = re.sub('[^a-zA-Z0-9 \n\.]', '_', string)
    return new_string


def get_issues_from_today():
    """Fetch a JSON file of issues according to filter"""
    issues = requests.get(
        settings.api_base_url + "/search?jql=" + settings.search_filter +
        "&fields=" + settings.fields,
        auth=(
            settings.username,
            settings.password
            )
        )
    return issues.json()


def send_survey(issue):
    """Send a an email to the reporter of an issue"""
    msg = MIMEText(
        'Hello!\n\n The Help Desk has recently closed your ticket, ' +
        sanitize(issue['fields']['summary']) +
        '. If you have a moment, please fill out this survey on how happy' +
        ' happy you are with your Help Desk experience.\n\n' +
        settings.google_form_link + '?entry.' +
        'settings.ticket_number_field' + '=' +
        issue['key'] + '\n\nThanks!\nThe Help Desk Staff'
        )
    msg['Subject'] = "Help Desk Survey for Ticket " + issue['key']
    msg['From'] = settings.from_address
    msg['To'] = issue['fields']['reporter']['emailAddress']
    mail = smtplib.SMTP(settings.smtp_server)
    mail.sendmail(
        settings.from_address,
        [issue['fields']['reporter']['emailAddress']],
        msg.as_string()
        )


def add_label(issue_key):
    """Add a label indicating that a survey has been sent to the requestor"""
    json_data = json.dumps({"update": {"labels": [{"add": "survey_sent"}]}})
    headers = {'Content-Type': 'application/json', }
    requests.put(
        url=settings.api_base_url + '/issue/' + issue_key,
        data=json_data,
        auth=(
            settings.username,
            settings.password
            ),
        headers=headers
        )

for ticket in get_issues_from_today()['issues']:
    if ('survey_sent' not in ticket['fields']['labels'] and
            validate_email(ticket['fields']['reporter']['emailAddress'])):
        send_survey(ticket)
        add_label(ticket['key'])
