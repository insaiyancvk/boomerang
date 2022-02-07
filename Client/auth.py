import sys,  json, os, flask, logging
from threading import Timer
from werkzeug.utils import secure_filename

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

CLIENT_SECRETS_FILE = "credentials.json"

SCOPES = [
    # 'https://www.googleapis.com/auth/gmail.readonly',
    # 'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    # 'https://www.googleapis.com/auth/gmail.addons.current.action.compose'
    ]

API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

app = flask.Flask(__name__, template_folder='.')
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def home():
    return flask.redirect('/authorize')

@app.route('/upload')
def upload_page():
   return flask.render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if flask.request.method == 'POST':
      f = flask.request.files['file']
      f.save(secure_filename(f.filename))
      return flask.redirect('/authorize')

@app.route('/authorize')
def authorize():

    if not os.path.exists(CLIENT_SECRETS_FILE):
        return flask.redirect('/upload')
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = CLIENT_SECRETS_FILE
    
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES)
        
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true')

    flask.session['state'] = state
    return flask.redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    
    state = flask.session['state']

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
    flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

    authorization_response = flask.request.url
    flow.fetch_token(authorization_response=authorization_response)
    
    credentials = flow.credentials
    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.redirect(flask.url_for('test_api_request'))

@app.route('/test')
def test_api_request():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

    credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

    service = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)
    
    service.users().drafts().list(userId='me').execute()

    flask.session['credentials'] = credentials_to_dict(credentials)

    with open('token.json','w') as f:
        json.dump(credentials_to_dict(credentials), f)

    return flask.redirect('/shutdown')

@app.route('/shutdown')
def shutdown():
    shutdown_server()
    return "Authorization flow completed. You can close the browser"

def shutdown_server():
    func = flask.request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def open_browser():
    if sys.platform == 'win32':
        os.startfile('http://localhost:5000')
    elif sys.platform == 'linux':
        subprocess.call(['xdg-open','http://localhost:5000'])

def start_auth():
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
    app.secret_key = 'sup GHIJKLMNOPQRSTUVWXYZ'
    app.config['SESSION_TYLE'] = 'filesystem'
    Timer(1, open_browser).start()
    app.run('localhost', 5000, threaded = True)