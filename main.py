import base64
import os
import csv
import argparse
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# OAuth2 scope for Gmail API
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

# Authenticate and create the Gmail API service
def authenticate_gmail():
    creds = None
    # Load existing token or initiate authentication
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

# Create an email message with HTML content
def create_message(sender, to, subject, html_content):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    message.attach(MIMEText(html_content, 'html'))
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    return {'raw': raw_message}

# Send an email message via Gmail API
def send_email(service, user_id, message):
    try:
        sent_message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f"Message Id: {sent_message['id']} sent successfully.")
        return sent_message
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None

# Send HTML email to multiple recipients
def send_email_to_list(sender, recipients, subject, html_content):
    service = authenticate_gmail()
    for recipient in recipients:
        message = create_message(sender, recipient, subject, html_content)
        send_email(service, 'me', message)

# Load recipient emails from a CSV file
def load_recipients_from_csv(file_path):
    recipients = []
    with open(file_path, newline='\n') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            recipients.append(row[0].strip())  # Assuming each row contains a single email address
    return recipients

# Load HTML content from a file
def load_html_content(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

# Main function to parse arguments and send emails
def main():
    parser = argparse.ArgumentParser(description="Send emails using Gmail API")
    parser.add_argument('--csv', required=True, help="NON HAI MESSO IL CSV '--csv recipients.csv'")
    parser.add_argument('--body', required=True, help="NON HAI MESSO IL BODY '--body body.html'")
    parser.add_argument('--subject', required=True, help="NON HAI MESSO IL SUBJECT '--subject 'Subject of the email'")    
    args = parser.parse_args()

    # Sender's email address
    sender_email = "info@onebridgetoidomeni.com"

    # Load recipients, subject, and body content
    recipient_list = load_recipients_from_csv(args.csv)
    subject = args.subject
    html_content = load_html_content(args.body)

    # Send email to recipients
    send_email_to_list(sender_email, recipient_list, subject, html_content)

if __name__ == '__main__':
    main()