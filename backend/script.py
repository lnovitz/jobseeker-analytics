import os
import json
import base64
import email
from datetime import datetime
from typing import List, Dict, Optional
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import pandas as pd

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailDataCollector:
    def __init__(self, credentials_path: str = 'credentials.json'):
        """
        Initialize the Gmail data collector.
        
        Args:
            credentials_path: Path to the Google OAuth credentials file
        """
        self.credentials_path = credentials_path
        self.service = self._get_gmail_service()
        
    def _get_gmail_service(self):
        """Set up Gmail API service with authentication."""
        creds = None
        
        # Check if token.json exists (saved credentials)
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
            
        # If no valid credentials, get new ones
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                creds = flow.run_local_server(port=50089)
                
            # Save credentials for future use
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
                
        return build('gmail', 'v1', credentials=creds)
    
    def search_emails(self, query: str, after_date: str = "2024/01/01") -> List[str]:
        """
        Search for all email message IDs matching the query and after a given date.
        Handles pagination to retrieve all results.
        Returns a list of message IDs.
        """
        all_message_ids = []
        page_token = None
        # Add date filter to query
        full_query = f"{query} after:{after_date.replace('-', '/')}"
        while True:
            response = self.service.users().messages().list(
                userId='me',
                q=full_query,
                maxResults=500,  # Gmail API max is 500
                pageToken=page_token
            ).execute()
            messages = response.get('messages', [])
            all_message_ids.extend([msg['id'] for msg in messages])
            page_token = response.get('nextPageToken')
            if not page_token:
                break
        return all_message_ids
    
    def get_email_content(self, message_id: str) -> Dict:
        """
        Get the full content of an email.
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Dictionary containing email content and metadata
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Get email headers
            headers = message['payload']['headers']
            subject = next(h['value'] for h in headers if h['name'] == 'Subject')
            sender = next(h['value'] for h in headers if h['name'] == 'From')
            date = next(h['value'] for h in headers if h['name'] == 'Date')
            
            # Get email body
            if 'parts' in message['payload']:
                parts = message['payload']['parts']
                body = ''
                for part in parts:
                    if part['mimeType'] == 'text/plain':
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                    elif part['mimeType'] == 'text/html':
                        html = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        soup = BeautifulSoup(html, 'html.parser')
                        body = soup.get_text()
            else:
                body = base64.urlsafe_b64decode(
                    message['payload']['body']['data']
                ).decode('utf-8')
            
            return {
                'id': message_id,
                'subject': subject,
                'sender': sender,
                'date': date,
                'body': body
            }
            
        except Exception as e:
            print(f"Error getting email content: {e}")
            return {}
    
    def load_labeled_message_ids(self, output_file: str = 'training_data.json') -> set:
        """
        Load already labeled message IDs from the output file.
        """
        if not os.path.exists(output_file):
            return set()
        with open(output_file, 'r') as f:
            try:
                data = json.load(f)
                return set(email['id'] for email in data if 'id' in email)
            except Exception:
                return set()
    

    def collect_training_data(self, output_file: str = 'training_data.json'):
        """
        Collect and label training data from Gmail, skipping already labeled messages.
        """

        # Search query for job application related emails
        with open("start_date_query.txt", "r") as f:
            query = f.read()
        
        # Get all message IDs since Jan 1, 2024
        message_ids = self.search_emails(query, after_date="2024/01/01")
        labeled_ids = self.load_labeled_message_ids(output_file)
        training_data = []
        if os.path.exists(output_file):
            with open(output_file, 'r') as f:
                training_data = json.load(f)
        print(f"Found {len(message_ids)} potential job application emails since 2024-01-01")
        statuses = [
            "false positive",
            "rejected",
            "no response",
            "request for availability",
            "interview scheduled",
            "offer"
        ]
        for i, msg_id in enumerate(message_ids, 1):
            if msg_id in labeled_ids:
                print(f"Skipping already labeled message {msg_id}")
                continue
            email_data = self.get_email_content(msg_id)
            if not email_data:
                continue
            print(f"\nEmail {i}/{len(message_ids)}")
            print(f"Subject: {email_data['subject']}")
            print(f"From: {email_data['sender']}")
            print(f"Date: {email_data['date']}")
            print("\nBody preview:")
            print(email_data['body'][:200] + "...")
            
            # Get user input for labeling
            while True:
                print("\nPossible statuses:")
                for j, status in enumerate(statuses, 1):
                    print(f"{j}. {status}")
                print("0. Skip this email")
                
                try:
                    choice = int(input("\nEnter the number corresponding to the application status: "))
                    if 0 <= choice <= len(statuses):
                        email_data['application_status'] = statuses[choice - 1]
                        training_data.append(email_data)
                        break
                    else:
                        print("Invalid choice. Please try again.")
                except ValueError:
                    print("Please enter a valid number.")
            
            # Save progress after each email
            with open(output_file, 'w') as f:
                json.dump(training_data, f, indent=2)
            
            print(f"\nProgress saved. {len(training_data)} emails labeled so far.")
            
        print(f"\nData collection complete. {len(training_data)} emails labeled.")
        print(f"Data saved to {output_file}")
        
        # Convert to CSV for easier analysis
        df = pd.DataFrame(training_data)
        csv_file = output_file.replace('.json', '.csv')
        df.to_csv(csv_file, index=False)
        print(f"Data also saved to {csv_file}")

def main():
    # Initialize the collector
    collector = GmailDataCollector()
    
    # Start collecting data
    collector.collect_training_data()

if __name__ == "__main__":
    main()