from datetime import datetime
import requests, os, json, msvcrt, time, sys
from auth import SCOPES
from auth import start_auth
from datepicker import formatted_datetime

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google.auth.exceptions import DefaultCredentialsError
from googleapiclient.discovery import build

from rich.table import Table
from rich.console import Console

def get_local_ip():
    import subprocess as sp

    out = sp.getoutput('arp -a')

    details = []
    for i in out.split('\n'):
        details.append(i.split())

    ips = []

    for i in details:
        if len(i) != 0 and i[0] != 'Interface:' and i[0] != 'Internet' and i[2] == 'dynamic':
            ips.append(i[0])

    return ips

def get_server_ip():

    if not os.path.exists('SERVERIP'):
    
        ips = get_local_ip()

        ips = [f'http://{i}:5000/' for i in ips]

        print('Searching for server...')

        SERVERIP = None

        for i in ips:
            try:
                if requests.get(i).text == 'Sup GAMER':
                    SERVERIP = i
                    print(f'Server found.\nServer IPv4: {SERVERIP}\n')
                    break
            except:
                continue
        
        if not SERVERIP:
            print('Server not found on LAN. Exiting.')
            exit()

        else:
            with open('SERVERIP','w') as f:
                _ = f.write(SERVERIP)

            print('\nConnected to the server\n')
            return SERVERIP
    else:

        with open('SERVERIP','r') as f:
            SERVERIP = f.read()
        
        if requests.get(SERVERIP).text == 'Sup GAMER':
            print('\nConnected to the server\n')
            return SERVERIP
        
        else:
            os.remove('SERVERIP')
            get_server_ip()


def requester(SERVER_IP_ADDRESS, date, draft_id):
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

def main():

    creds = None
    new = False

    if os.path.exists('token.json'): # Check if token.json exists in client's system
        creds = Credentials.from_authorized_user_file('token.json', SCOPES) # Load the credentials
    else:
        new = True
        start_auth()

    if not creds or not creds.valid: # Check if the token is valid
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
    else:
        start_auth() # Create a token by completing auth flow

    SERVER_IP_ADDRESS = get_server_ip()

    if new and (requests.get(SERVER_IP_ADDRESS+'checkToken').status_code == 200):
        requests.get(SERVER_IP_ADDRESS+'remToken')

    if requests.get(SERVER_IP_ADDRESS+'checkToken').status_code == 404: # Check if token.json exists in server
        with open('token.json', 'r') as f:
            requests.post(SERVER_IP_ADDRESS+'authtoken', json = json.load(f)) # make a post request and send token.json

    try:
        service = build('gmail', 'v1', credentials=creds)
    except DefaultCredentialsError:
        main()  

    print('Reading the drafts...')

    time.sleep(3)

    try:
        drafts = [i['id'] for i in list_drafts(service)['drafts']]
    except KeyError:
        print("No drafts found. Exiting.")
        sys.exit()

    n = 1
    for i in drafts:

        clear_screen()

        if i in eval(requests.get(SERVER_IP_ADDRESS+'getscheduleid').text):
            continue

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

        if not receiver:
            print('Receiver field can\'t be empty. This draft is not scheduled.')
            time.sleep(5)
            continue
        
        print('\n\t\tPress "enter" or "space" to select date and time\n\n\t\tOr any other key to skip this draft')
        sel = msvcrt.getch()

        if sel in (b' ', b'\r'):

            flag = True

            while flag:

                seldatetime = formatted_datetime()

                stime = datetime.strptime(str(seldatetime), '%Y-%m-%dT%H:%M')

                if stime.hour > datetime.now().hour or (stime.hour == datetime.now().hour and stime.minute > datetime.now().minute):
                    requester(SERVER_IP_ADDRESS,seldatetime, i)
                    flag = False
                
                elif stime.hour < datetime.now().hour or (stime.hour == datetime.now().hour and stime.minute < datetime.now().minute):
                    print(f'\nPlease enter future time for schedule.\nTime you entered - {stime.hour}:{stime.minute}\nTime right now - {datetime.now().hour}:{datetime.now().minute}\n')
                    time.sleep(2)

        n += 1

    clear_screen()
    print('All mails have been scheduled for the selected date and time.')
    sys.exit()

if __name__ == '__main__':
    
    main()