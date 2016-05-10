# service_desk_survey_sender
Sends an email from Google Forms to requestor on recently closed JIRA tickets

# Setup
1. Create a Google form, with a field called "Ticket Number"
2. View the live Google form, and find the html for the ticket number field. Copy the entryid
3. Create a user with permissions to access the JIRA project via API
4. Make sure the default screen for the project includes the "Labels" field
5. Copy settings.py.sample to settings.py
6. Populate the settings.py with appropriate values
7. Put somewhere and attach it to a periodic cronjob