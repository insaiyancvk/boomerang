## Required dependencies

```
pip3 install tkcalendar tkTimePicker --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib flask rich
```

## Register an app on Google API console
- Start [here](https://console.developers.google.com/home/dashboard)
- Select 'NEW PROJECT'
- Give some name to the project (Ex: boomerang).
- Leave the location as 'No organization'.
- Select the created project.
- Click [this](https://console.developers.google.com/marketplace/product/google/gmail.googleapis.com) link and 'ENABLE' gmail API.
- Go to [OAuth consent screen](https://console.developers.google.com/apis/credentials/consent) and select 'External'
    - Give a name to the app
    - Select your gmail for 'User support email'
    - Scroll down and enter your gmail under 'Developer contact information'
    - Then 'Save and Continue'
    - Click 'Add or remove scopes'
        - Search for 'send' next to Filter and select (look for it under Scope column)
            - '.../auth/gmail.compose'
        - Select 'Update'
    - Click on 'Save and continue'
    - For test users, add gmail id of the person who wants to use the scheduler. (Ex: yourself@gmail.com)
        - Click on 'Add users' and enter the gmail id.
        - Click on 'Add' twice.
    - Click on 'Save and continue'
    - 
- Go to [credentials](https://console.developers.google.com/apis/credentials) and select 'Create Credentials'
    - Select 'OAuth client ID'
    - Select 'Desktop app' for the application type
    - Enter some name for the desktop client(Ex: Desktop client 1).
    - Click on `Download json` from the pop up 'OAuth client created' and name the file as 'credentials'
    - If The pop up is not found, then 
        - Download from [credentials](https://console.developers.google.com/apis/credentials), under OAuth 2.0 Client IDs
        - Under actions column, click on 'download' icon and name the file as 'credentials'
- Put this `credentials.json` file in boomerang/Client directory
    - Or the program itself asks you to select the file when you run it.

>**NOTE: NEVER MISPLACE _CREDENTIALS.JSON_ AS IT CONTAINS SENSITIVE INFORMATION THAT IS LINKED TO YOUR GOOGLE ACCOUNT**

## How to run

- Clone the repository

``` git clone https://github.com/insaiyancvk/boomerang ```

- Change the directory

``` cd Client ```

- Run the Script

``` [python3/python/py] client.py ```

## Everytime you want to schedule a mail

- Open command prompt and change the directory to the Client directory
- Run the code using `py client.py`