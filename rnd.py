# https://pypi.org/project/schedule/
# https://pythonrepo.com/repo/DigonIO-scheduler

# from calendar import month
# import os
# from datetime import datetime
# from sched import scheduler
# from flask import Flask, request
# from flask_restful import reqparse
# from apscheduler.schedulers.background import BackgroundScheduler
# from flask_sqlalchemy import SQLAlchemy
# # import sqlalchemy

# db_path = os.path.abspath(os.getcwd())+"\database.db"

# # initialize scheduler with your preferred timezone
# scheduler = BackgroundScheduler({'apscheduler.timezone': 'Asia/Calcutta'})
# scheduler.add_jobstore('sqlalchemy', url=f'sqlite:///{db_path}')
# scheduler.start()

# schedule_app = Flask(__name__)
# schedule_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+db_path
# db = SQLAlchemy(schedule_app)

# @schedule_app.route('/schedulePrint', methods=['POST'])
# def schedule_to_print():
#     parser = reqparse.RequestParser()  # initialize
#     # parser.add_argument('date', required=True)  # add args
#     parser.add_argument('time', required=True)
#     parser.add_argument('text', required=True)
    
#     data = parser.parse_args()  # parse arguments to dictionary
#     # print(data)
    
#     time = data['time']
#     text = data['text']
#     #convert to datetime
#     date_time = datetime.strptime(str(time), '%Y-%m-%dT%H:%M')
#     #schedule the method 'printing_something' to run the the given 'date_time' with the args 'text'
    
#     job = scheduler.add_job(
#         printing_something, 
#         trigger='date', 
#         next_run_time=str(date_time),
#         args=[text])

#     return "job details: %s" % job

# @schedule_app.route('/getJobs', methods=['GET'])
# def getJobs():
#   jobs = scheduler.get_jobs()
#   print(jobs)
#   return 200

# def printing_something(text):
#     print("printing %s at %s" % (text, datetime.now()))

# # schedule_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbdir/text'
# schedule_app.run(debug=True)






import os
import flask
import requests

import google.oauth2.credentials
import google_auth_oauthlib.flow
import googleapiclient.discovery

CLIENT_SECRETS_FILE = "credentials.json"

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.addons.current.action.compose'
    ]

API_SERVICE_NAME = 'gmail'
API_VERSION = 'v1'

app = flask.Flask(__name__)

@app.route('/')
def index():
  return print_index_table()


@app.route('/test')
def test_api_request():
    if 'credentials' not in flask.session:
        return flask.redirect('authorize')

  # Load credentials from the session.
    credentials = google.oauth2.credentials.Credentials(
      **flask.session['credentials'])

    service = googleapiclient.discovery.build(
      API_SERVICE_NAME, API_VERSION, credentials=credentials)

    # print(f'\n\n\n\t\t\tAFTER BUILD CALL: {service}')
    # print(f'\n\n\n\t\t\tCREDENTIALS: {credentials}')
    
    files = service.users().drafts().list(userId='me').execute()

    flask.session['credentials'] = credentials_to_dict(credentials)

    return flask.jsonify(**files)

@app.route('/authorize')
def authorize():
  # Create flow instance to manage the OAuth 2.0 Authorization Grant Flow steps.
  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES)

  # The URI created here must exactly match one of the authorized redirect URIs
  # for the OAuth 2.0 client, which you configured in the API Console. If this
  # value doesn't match an authorized URI, you will get a 'redirect_uri_mismatch'
  # error.
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  authorization_url, state = flow.authorization_url(
      # Enable offline access so that you can refresh an access token without
      # re-prompting the user for permission. Recommended for web server apps.
      access_type='offline',
      # Enable incremental authorization. Recommended as a best practice.
      include_granted_scopes='true')

  # Store the state so the callback can verify the auth server response.
  flask.session['state'] = state
#   print(f'\n\n\n\t\t\tAUTHORIZATION URL : {authorization_url}\n\n\n')
#   print(f"\n\n\n\t\t\tSTATE: {state}\n\n\n")
  return flask.redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
  # Specify the state when creating the flow in the callback so that it can
  # verified in the authorization server response.
  state = flask.session['state']

  flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
      CLIENT_SECRETS_FILE, scopes=SCOPES, state=state)
  flow.redirect_uri = flask.url_for('oauth2callback', _external=True)

  # Use the authorization server's response to fetch the OAuth 2.0 tokens.
  authorization_response = flask.request.url
  flow.fetch_token(authorization_response=authorization_response)

  # Store credentials in the session.
  # ACTION ITEM: In a production app, you likely want to save these
  #              credentials in a persistent database instead.
  credentials = flow.credentials
  flask.session['credentials'] = credentials_to_dict(credentials)

  return flask.redirect(flask.url_for('test_api_request'))

@app.route('/clear')
def clear_credentials():
  if 'credentials' in flask.session:
    print("\n\n\n\t\t\t",flask.session['credentials'],"\n\n\n")
    del flask.session['credentials']
  return ('Credentials have been cleared.<br><br>' +
          print_index_table())

def credentials_to_dict(credentials):
  return {'token': credentials.token,
          'refresh_token': credentials.refresh_token,
          'token_uri': credentials.token_uri,
          'client_id': credentials.client_id,
          'client_secret': credentials.client_secret,
          'scopes': credentials.scopes}

def print_index_table():
  return ('<table>' +
          '<tr><td><a href="/test">Test an API request</a></td>' +
          '<td>Submit an API request and see a formatted JSON response. ' +
          '    Go through the authorization flow if there are no stored ' +
          '    credentials for the user.</td></tr>' +
          '<tr><td><a href="/authorize">Test the auth flow directly</a></td>' +
          '<td>Go directly to the authorization flow. If there are stored ' +
          '    credentials, you still might not be prompted to reauthorize ' +
          '    the application.</td></tr>' +
          '<tr><td><a href="/revoke">Revoke current credentials</a></td>' +
          '<td>Revoke the access token associated with the current user ' +
          '    session. After revoking credentials, if you go to the test ' +
          '    page, you should see an <code>invalid_grant</code> error.' +
          '</td></tr>' +
          '<tr><td><a href="/clear">Clear Flask session credentials</a></td>' +
          '<td>Clear the access token currently stored in the user session. ' +
          '    After clearing the token, if you <a href="/test">test the ' +
          '    API request</a> again, you should go back to the auth flow.' +
          '</td></tr></table>')


if __name__ == '__main__':
  # When running locally, disable OAuthlib's HTTPs verification.
  # ACTION ITEM for developers:
  #     When running in production *do not* leave this option enabled.
#   url = 'boomerang.rog'
#   app.config['SERVER_NAME'] = url   
  os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
  app.secret_key = 'sup H'
  app.config['SESSION_TYLE'] = 'filesystem'

  # Specify a hostname and port that are set as a valid redirect URI
  # for your API project in the Google API Console.
  app.run('0.0.0.0', 5000, debug=True, threaded=True)