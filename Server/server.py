from datetime import datetime
import os, json

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

db_path = os.path.abspath(os.getcwd())+"\database.db"
scheduler = BackgroundScheduler({'apscheduler.timezone': 'Asia/Calcutta'})
scheduler.add_jobstore('sqlalchemy', url=f'sqlite:///{db_path}')
scheduler.start()

SCOPES = [
    # 'https://www.googleapis.com/auth/gmail.readonly',
    # 'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    # 'https://www.googleapis.com/auth/gmail.addons.current.action.compose'
    ]

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+db_path
db = SQLAlchemy(app)

@app.route('/')
def saiyan():
    return "Sup GAMER"

@app.route('/checkToken')
def checkToken():
    if not os.path.exists('token.json'):
        return 'Token file not found',404
    else:
        return 'Token exists in server.',200

@app.post('/authtoken')
def gettoken():
    
    tokenfile = request.get_json()

    with open('token.json', 'w') as f:
        json.dump(tokenfile, f)
    
    return 'Token file saved successfully.',201

@app.get('/remToken')
def remToken():

    if os.path.exists('token.json'):
        os.remove('token.json')
    
    return 'Token removed from server.', 201

@app.post('/boomerang')
def boomerang():

    if not os.path.exists('token.json'):
        return 'Token not found.',404

    data = request.get_json()

    time = data['time']
    draft_id = data['draft_id']

    # print(time, draft_id)

    date_time = datetime.strptime(str(time), '%Y-%m-%dT%H:%M')

    scheduler.add_job(
        send_draft,
        trigger='date',
        next_run_time=str(date_time),
        args=[draft_id]
    )

    return 'Boomerang scheduled Successfully', 201

def send_draft(draft_id):
    
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    service = build('gmail', 'v1', credentials=creds)

    return service.users().drafts().send(
    userId='me',
    body = {'id': draft_id}
    ).execute()

if __name__ == '__main__':
    app.run(
        '0.0.0.0', 
        5000, 
        threaded = True, 
        # debug=True
        )