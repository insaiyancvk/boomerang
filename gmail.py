from __future__ import print_function
import json

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.addons.current.action.compose'
    ]


creds = None

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)

        creds = flow.run_local_server(port=0)
        
    with open('templates/token.json', 'w') as token:
        token.write(creds.to_json())
        
spam = {}

with open('spam.json','r') as f:
    spam = json.load(f)

id = spam['drafts'][0]['id']

service = build('gmail', 'v1', credentials=creds)

def json_pretty_print(obj):
  print(json.dumps(obj,indent=3))

def send_draft(draft_id):
    return service.users().drafts().send(
    userId='me',
    body = {'id': draft_id}
    ).execute()

def get_draft_details(draft_id, format = 'minimal'):
    """
    format: 
      full
      metadata
      minimal 
      raw
    """

    return service.users().drafts().get(
        userId='me',
        id=draft_id,
        format=format).execute()

def list_drafts():
    """
    returns all the saved drafts
    """
    return service.users().drafts().list(
        userId='me').execute()

# json_pretty_print(list_drafts())