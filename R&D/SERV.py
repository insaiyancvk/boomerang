from datetime import datetime
from flask import Flask, request, redirect, render_template, url_for, session, jsonify
# from pandas import ExcelWriter
from werkzeug.utils import secure_filename
# from urllib.parse import urlparse
# import ipaddress
import socket
from flask_restful import reqparse
import os, json
# from flask_apscheduler import APScheduler
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
# from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import Flow

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.addons.current.action.compose'
    ]

db_path = os.path.abspath(os.getcwd())+"\database.db"
scheduler = BackgroundScheduler({'apscheduler.timezone': 'Asia/Calcutta'})
scheduler.add_jobstore('sqlalchemy', url=f'sqlite:///{db_path}')
scheduler.start()

app = Flask(__name__, template_folder='templates')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+db_path
db = SQLAlchemy(app)

IP_ADDRESS = socket.gethostbyname(socket.gethostname())

@app.route('/')
def saiyan():
    return "Sup GAMER"

@app.route('/checkCreds')
def checkcreds():
    if os.path.exists('credentials.json'):
        return "credentials.json exists."
    else:
        return redirect('/upload')

@app.route('/upload')
def upload():
   return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      f.save(secure_filename(f.filename))
      return 'file uploaded successfully'

@app.route('/checkToken')
def checkToken():
    if 'credentials' not in session:
        return redirect('/authorize')
    else:
        return "Using existing cookies."

@app.route('/clear')
def remToken():
    if 'credentials' in session:
        del session['credentials']
        return 'Credentials have been cleared.'

@app.route('/boomerang', methods = ['POST']) 
def boomerang():
    
    if request.method == 'POST':

        if not os.path.exists('token.json'):
            return redirect('/authorize')
        
        creds = Credentials(**session['credentials'])

        parser = reqparse.RequestParser()  # initialize
        parser.add_argument('time', required=True)  # add args
        parser.add_argument('draft_id', required=True)
        
        data = parser.parse_args()  # parse arguments to dictionary

        time = data['time']
        draft_id = data['draft_id']

        date_time = datetime.strptime(str(time), '%Y-%m-%dT%H:%M')

        service = build('gmail', 'v1', credentials=creds)

        scheduler.add_job(
            send_draft,
            trigger='date',
            next_run_time=str(date_time),
            args = [service, draft_id]
        )

        return 'Boomerang scheduled added successfully.', 200  # return data with 200 OK

@app.route('/authorize')
def authorize():
    # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
    if os.path.exists('credentials.json'):
        flow = Flow.from_client_secrets_file(
            'credentials.json', scopes=SCOPES)
    else:
        return redirect('/upload')

    # The URI created here must exactly match one of the authorized redirect URIs
    # for the OAuth 2.0 client, which you configured in the API Console. If this
    # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
    # error.
    #   flow.redirect_uri = url_for('oauth2callback', _external=True)
    #   print(f"\n\n\nURLFOR OAUTH2CALLBACK:\T{url_for('oauth2callback', _external=True)}\n\n\n")
    flow.redirect_uri = "http://localhost:5000/oauth2callback"

    authorization_url, state = flow.authorization_url(
        # Enable offline access so that you can refresh an access token without
        # re-prompting the user for permission. Recommended for web server apps.
        access_type='offline',
        # Enable incremental authorization. Recommended as a best practice.
        include_granted_scopes='true')

    # Store the state so the callback can verify the auth server response.
    session['state'] = state

    #   print(flow.redirect_uri)
    #   print(authorization_url)
    print(state)

    return {'auth_url':authorization_url, 
                'state':state}

@app.route('/oauth2callbacc', methods = ['POST'])
def oauth2callbacc():

    if request.method == 'POST':

        args = request.get_json()
        print(args)
        state = args['state']
        session['state'] = state
        redirecturl = args['redirecturl']

        print(f'\n\n\n ARGS\t{args}')
        print(f"\n\n\n REDIRECTURL\t{args['redirecturl']}\n\n")

        flow = Flow.from_client_secrets_file(
            'credentials.json', scopes=SCOPES, state=state)
        
        flow.redirect_uri = url_for('oauth2callback', _external=True)

        # flow.fetch_token(authorization_response=redirecturl)
        
        # with open('token.json', 'w') as f:
        #     json.dump(credentials_to_dict(flow.credentials), f)

        # Flow.from_client_secrets_file(
        #         'credentials.json', scopes=SCOPES, state=state).fetch_token(authorization_response=redirecturl)
        
        # session['state'] = state
        return redirect(redirecturl)

@app.route('/oauth2callback')
def oauth2callback():
    # Specify the state when creating the flow in the callback so that it can
    # verified in the authorization server response.
    #   state = session['state']
    # if request.method == 'POST':
        
        # parser = reqparse.RequestParser()  # initialize
        # parser.add_argument('state', required=True)  # add args
        # args = parser.parse_args()  # parse arguments to dictionary

        # state = args['state']
        state = session['state']

        print(f"\n\n\SESSION['STATE']:\t{session['state']}\n\n")


        # print(f"\n\n\ARGS['STATE']:\t{args['state']}\n\n")

        flow = Flow.from_client_secrets_file(
            'credentials.json', scopes=SCOPES, state=state)
        flow.redirect_uri = url_for('oauth2callback', _external=True)

        print(f"\n\n\n{flow.redirect_uri}\n\n\n")

        # Use the authorization server's response to fetch the OAuth 2.0 tokens.
        authorization_response = request.url

        print(f"\n\n\nARGS.GET STATE    {request.args.get('state')}\n")

        # authorization_response = request.url.replace(IP_ADDRESS, 'localhost')
        # if request.args.get('state') != None:
        #     authorization_response = authorization_response.replace(request.args.get('state'), state)
        print(f"\n\n\nauth response\t{authorization_response}\n\n\n")


        # print(f"\n\n{flow}\n\n")
        flow.fetch_token(authorization_response=authorization_response)

        # Store credentials in the session.
        # ACTION ITEM: In a production app, you likely want to save these
        #              credentials in a persistent database instead.
        credentials = flow.credentials
        session['credentials'] = credentials_to_dict(credentials)
        print(credentials_to_dict(credentials))
        with open('token.json', 'w') as f:
            json.dump(credentials_to_dict(credentials), f)

        return redirect(url_for('test_api_request'))

@app.route('/gettoken', methods = ['POST'])
def gentoken():
    parser = reqparse.RequestParser()  # initialize
    parser.add_argument('state', required=True)  # add args
    args = parser.parse_args()  # parse arguments to dictionary

    state = args['state']

    flow = Flow.from_client_secrets_file(
      'credentials.json', scopes=SCOPES, state=state)
    flow.redirect_uri = url_for('oauth2callback', _external=True)

    # authorization_response = f"http://localhost:5000/oauth2callback?state={state}&code=4/0AX4XfWh0YukzrTv_N4GmnSt4YfL6OGL9dVHf4KVm-VcCpwPbymqnLU6b2fzOwdSW663sSQ&scope=https://www.googleapis.com/auth/gmail.readonly%20https://www.googleapis.com/auth/gmail.addons.current.action.compose%20https://www.googleapis.com/auth/gmail.send%20https://www.googleapis.com/auth/gmail.compose"


    authorization_response = request.url.replace('localhost', IP_ADDRESS).replace(request.args.get('state'), state)

    flow.fetch_token(authorization_response=authorization_response)

    credentials = flow.credentials
    # session['credentials'] = credentials_to_dict(credentials)
    # print(credentials_to_dict(credentials))
    with open('token.json', 'w') as f:
        json.dump(credentials_to_dict(credentials), f)

    return redirect(url_for('test_api_request'))


@app.route('/test')
def test_api_request():
    
    # print(request.args.get('state'), session.get('_google_authlib_state_'))
    if not os.path.exists('token.json'):
        return redirect('authorize')

    with open('token.json') as f:
        creds = json.load(f)
        
    credentials = Credentials(**creds)

    service = build("gmail", "v1", credentials=credentials)
    
    files = service.users().drafts().list(userId='me').execute()

    # session['credentials'] = credentials_to_dict(credentials)

    return "Authorization and testing completed.<br>You can continue using Boomerang :)", 201


def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def send_draft(service, draft_id):
    return service.users().drafts().send(
    userId='me',
    body = {'id': draft_id}
    ).execute()

if __name__ == '__main__':
    # url = 'insaiyancvk.me:5000'
    # app.config['SERVER_NAME'] = url
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    app.secret_key = 'supersecretkeydontreadthis'
    app.config['SESSION_TYLE'] = 'filesystem'
    
    app.run(debug=True, threaded=True, host="0.0.0.0", port=5000)