## Required dependencies
>Run the following command with superuser privileges the server is on linux

```
pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib flask flask_sqlalchemy apscheduler
```

## How to get the script?

1. You can clone the entire repository with:

``` git clone https://github.com/insaiyancvk/boomerang ```

- Change into the server directory:

``` cd Server ```

- Run the script

``` python server.py ```

2. Curl the server script (Recommended):

``` curl -o server.py https://raw.githubusercontent.com/insaiyancvk/boomerang/main/Server/server.py && python3 server.py ```

- Run the script

``` python server.py ```

## Setup the script to autostart on boot
_Assuming your server is RPi_

- Copy the `server.py` file to /etc/init.d/
    - Ex: `sudo cp /home/pi/boomerang/server.py /etc/init.d/`
- Change to init.d directory:
    - Ex: `cd /etc/init.d`
- Make the script executable by changing its permission
    - Ex: `sudo chmod+x server.py`
- Run the following command
    - `sudo update-rc.d server.py defaults`
- Reboot Pi
    - `sudo reboot`