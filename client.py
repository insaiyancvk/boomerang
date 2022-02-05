import requests, os, json, msvcrt
from auth import SCOPES
from auth import start_auth
from datepicker import formatted_datetime

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from rich.table import Table
from rich.console import Console

SERVER_IP_ADDRESS = 'http://192.168.1.7:5000/' # TODO: automatically scan all the dynamic ip adresses on LAN and detect the server

def get_local_ip():
    import subprocess as sp

    out = sp.getoutput('arp -a')

    details = []
    for i in out.split('\n'):
        details.append(i.split())

    arp = {
        'Internet Address': [],
        'Physical Address': [],
        'Type': []
    }

    for i in details:
        if len(i) != 0 and i[0] != 'Interface:' and i[0] != 'Internet':
            arp['Internet Address'].append(i[0])
            arp['Physical Address'].append(i[1])
            arp['Type'].append(i[2])

    return arp

def requester(date, draft_id):
    boomerang_endpoint = f"{SERVER_IP_ADDRESS}boomerang"
    requests.post(url=boomerang_endpoint, json = {'time':date, 'draft_id':draft_id})

def list_drafts(service):
    """
    returns all the saved drafts
    """
    return service.users().drafts().list(
        userId='me').execute()

def get_draft_details(service, draft_id, format = 'minimal'):
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

def clear_screen():
    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'posix':
        os.system('clear')

if __name__ == '__main__':

    creds = None

    if os.path.exists('token.json'): # Check if token.json exists in client's system
        creds = Credentials.from_authorized_user_file('token.json', SCOPES) # Load the credentials
    
    if not creds or not creds.valid: # Check if the token is valid
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    else:
        start_auth() # Create a token by completing auth flow

    if requests.get(SERVER_IP_ADDRESS+'/checkToken').status_code == 404: # Check if token.json exists in server
        with open('token.json', 'r') as f:
            requests.post(SERVER_IP_ADDRESS+'authtoken', json = json.load(f)) # make a post request and send token.json

    service = build('gmail', 'v1', credentials=creds)

    print('Reading the drafts...')

    drafts = [i['id'] for i in list_drafts(service)['drafts']]

    # print(drafts)

    n = 1
    for i in drafts:

        subject, receiver = 'None', 'None'

        details = get_draft_details(service, i, 'metadata')

        if details['message']['payload']['headers'][3]['value'] != '':
            subject = details['message']['payload']['headers'][3]['value']
        
        if details['message']['payload']['headers'][5]['name'] == 'To':
            receiver = details['message']['payload']['headers'][5]['value']
        
        table = Table(show_header=True, header_style="bold cyan")

        table.add_column("Draft no.")
        table.add_column("Subject")
        table.add_column("Receiver")
        table.add_row(str(n), subject, receiver)
        Console().print('\t\t',table)
        
        print('Press a key to select date and time')
        _ = msvcrt.getch()

        seldatetime = formatted_datetime()
        requester(seldatetime, i)

        n += 1
        clear_screen()