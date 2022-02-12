from datetime import datetime
import os, json

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

db_path = os.path.abspath(os.getcwd())+"\\database.db"
scheduler = BackgroundScheduler({'apscheduler.timezone': 'Asia/Calcutta'})
scheduler.add_jobstore('sqlalchemy', url=f'sqlite:///{db_path}')
scheduler.start()

SCOPES = [
    'https://www.googleapis.com/auth/gmail.compose',
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

    #TODO: ADD 30S TO SCHEDULES THAT HAVE SAME TIME

    date_time = datetime.strptime(str(time), '%Y-%m-%dT%H:%M')

    scheduler.add_job(
        send_draft,
        trigger='date',
        next_run_time=str(date_time),
        args=[draft_id],
        id = draft_id
    )

    return 'Boomerang scheduled Successfully', 201

@app.get('/getscheduleid')
def getscheduleid():

    return jsonify([str(i.id) for i in scheduler.get_jobs()])

@app.get('/getJobs')
def getJobs():
    
    job_obj = scheduler.get_jobs()
    jobids = [str(i.id) for i in job_obj]
    
    scheduletime = [ f"{str(i.next_run_time.day)}-{str(i.next_run_time.month)}-{str(i.next_run_time.year)}"+"\n"+str(datetime.strptime(str(i.next_run_time.hour)+":"+str(i.next_run_time.minute), "%H:%M").strftime("%I:%M %p")) for i in job_obj]

    job_time = {}

    for i in range(len(job_obj)):
        job_time[jobids[i]] = scheduletime[i]

    return job_time

@app.post('/editJobs')
def editJobs():
    
    data = request.get_json()

    id = data['id']
    mtime = data['time']

    date_time = datetime.strptime(str(mtime), '%Y-%m-%dT%H:%M')

    scheduler.modify_job(job_id=id, next_run_time = date_time)

    return '',200

@app.post('/remJob')
def remJob():

    draft_id = request.get_json()['id']

    scheduler.remove_job(job_id=draft_id)

    return '',200

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
        debug=True
        )