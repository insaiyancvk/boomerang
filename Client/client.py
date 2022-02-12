from datetime import datetime
import requests, os, json, msvcrt, time, sys
from auth import SCOPES
from auth import start_auth
from picker import Picker
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
        
        try:

            if requests.get(SERVERIP).text == 'Sup GAMER':
                print('\nConnected to the server\n')
                return SERVERIP
                
        except TimeoutError:
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

def schedule(SERVER_IP_ADDRESS,service):

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

        for j in details['message']['payload']['headers']:
            
                if j['name'] == 'Subject':
                    subject = j['value']
                elif j['name'] == 'To':
                    receiver = j['value']
        
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

                if stime > datetime.now():

                    import pdb; pdb.set_trace()

                    requester(SERVER_IP_ADDRESS,seldatetime, i)
                    flag = False

                else:

                    print(
                        f'\nPlease enter future time for schedule.',
                        f'\nTime you entered - {str(stime.day)+"-"+str(stime.month)+"-"+str(stime.year)+"  "+datetime.strptime(str(stime.hour)+":"+str(stime.minute), "%H:%M").strftime("%I:%M %p")}',
                        f'\nTime right now - {str(datetime.now().day)+"-"+str(datetime.now().month)+"-"+str(datetime.now().year)+"  "+datetime.strptime(str(datetime.now().hour)+":"+str(datetime.now().minute), "%H:%M").strftime("%I:%M %p")}\n')
                    time.sleep(2)

        n += 1

    clear_screen()
    print('All mails have been scheduled for the selected date and time.')
    sys.exit()

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
            requests.post(
                SERVER_IP_ADDRESS+'authtoken', 
                json = json.load(f)) # make a post request and send token.json

    try:
        service = build('gmail', 'v1', credentials=creds)
    except DefaultCredentialsError:
        main()  

    picker = Picker(
        [
            "Make a schedule",
            "Check scheduled mails",
            "Change scheduled date/time",
            "Remove a schedule"],

        "Select your choice using arrow keys or press q to quit", 
        indicator=" => ")

    picker.register_custom_handler(ord('q'), lambda picker: exit())
    picker.register_custom_handler(ord('Q'), lambda picker: exit())
    _,ch = picker.start()

    if ch == 0:

        schedule(SERVER_IP_ADDRESS, service)
    
    elif ch == 1:

        jobs = requests.get(SERVER_IP_ADDRESS+'getJobs').text

        # import pdb; pdb.set_trace()


        if len(eval(jobs)) == 0:
            print("No schedules found. Exiting.")
            sys.exit()

        n = 1

        table = Table(show_header=True, header_style="bold cyan")

        table.add_column("Draft no.")
        table.add_column("Subject")
        table.add_column("Receiver")
        table.add_column("Scheduled at")

        for draft_id, schedule_time in eval(jobs).items():

            details = get_draft_details(service, draft_id, 'metadata')
            
            for i in details['message']['payload']['headers']:
                if i['name'] == 'Subject':
                    subject = i['value']
                elif i['name'] == 'To':
                    receiver = i['value']

            
            table.add_row(str(n), subject, receiver, schedule_time+"\n")

            n += 1

        Console().print('\t\t',table)


    elif ch == 2:

        draft_ids = requests.get(SERVER_IP_ADDRESS+'getJobs').text

        draft_details = {}

        for draft_id in eval(draft_ids):

            details = get_draft_details(service, draft_id, 'metadata')

            for i in details['message']['payload']['headers']:
                if i['name'] == 'Subject':
                    subject = i['value']
                elif i['name'] == 'To':
                    receiver = i['value']

            draft_details[draft_id] = [subject, receiver]
        
        flag1 = True

        import pdb; pdb.set_trace()

        while flag1:

            p = Picker(
                [str(i[0]+" - "+i[1]+" scheduled at "+i[2].replace('\\n',' ')) for i in draft_details.values()],

                "Select your choice using arrow keys or press q to quit", 
                indicator=" => ")

            p.register_custom_handler(ord('q'), lambda p: exit())
            p.register_custom_handler(ord('Q'), lambda p: exit())
            _,c = p.start()

            flag = True

            while flag:

                seldatetime = formatted_datetime()

                stime = datetime.strptime(str(seldatetime), '%Y-%m-%dT%H:%M')

                if stime > datetime.now():

                    res = requests.post(
                        SERVER_IP_ADDRESS+'editJobs', 
                        json = {
                            'id': list(draft_details)[c], 
                            'time': seldatetime})
                    if res.status_code == 200:
                        print("Rescheduled successfully.")
                    flag = False

                else:

                    print(
                        f'\nPlease enter future time for schedule.',
                        f'\nTime you entered  {str(stime.day)+"-"+str(stime.month)+"-"+str(stime.year)+"  "+datetime.strptime(str(stime.hour)+":"+str(stime.minute), "%H:%M").strftime("%I:%M %p")}',
                        f'\nTime right now  {str(datetime.now().day)+"-"+str(datetime.now().month)+"-"+str(datetime.now().year)+"  "+datetime.strptime(str(datetime.now().hour)+":"+str(datetime.now().minute), "%H:%M").strftime("%I:%M %p")}\n')
                    time.sleep(2)

            print("Do you want to continue? (Y/N)")
            sel = msvcrt.getch()
            if sel.lower() == 'y':
                flag1 = True
            else:
                flag1 = False


    elif ch == 3:

        flag2 = True

        while flag2:

            draft_ids = requests.get(SERVER_IP_ADDRESS+'getJobs')
            draft_ids = eval(draft_ids.text)

            draft_details = {}

            for draft_id, time in draft_ids.items():

                details = get_draft_details(service, draft_id, 'metadata')

                for i in details['message']['payload']['headers']:
                    
                    if i['name'] == 'Subject':
                        subject = i['value']
                    elif i['name'] == 'To':
                        receiver = i['value']

                draft_details[draft_id] = [subject, receiver, time]

            import pdb; pdb.set_trace()


            p = Picker(
                [str(i[0]+" - "+i[1]+" scheduled at "+i[2].replace('\\n',' ')) for i in draft_details.values()],
                "Select your choice using arrow keys or press q to quit", 
                indicator=" => ")

            p.register_custom_handler(ord('q'), lambda p: exit())
            p.register_custom_handler(ord('Q'), lambda p: exit())
            _,c = p.start()

            res = requests.post(
                    SERVER_IP_ADDRESS+'remJob', 
                    json = {
                        'id': list(draft_details)[c]})
            
            if res.status_code == 200:
                print("Schedule removed successfully.")
            
            print("Do you want to continue? (Y/N)")
            sel = msvcrt.getch()

            if sel.lower() == 'Y':
                flag2 = True
            else:
                flag2 = False


if __name__ == '__main__':
    
    main()