from functools import wraps
from flask import Flask, request, render_template, redirect, url_for, Response
import subprocess
import argparse
import sys

USERNAME="root"
PASSWORD="root"

app = Flask(__name__)
is_playing = False

def check_auth(username, password):
    return username == USERNAME and password == PASSWORD

def authenticate():
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 
        401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@app.route('/')
@requires_auth
def index():
    return render_template('index.html')


@app.route('/command', methods=['POST'])
def command():
    cmd = request.form['command']   
    subprocess.run(['osascript', 'commands/spotify.scpt', cmd])
    return redirect(url_for('index'))
  

if __name__ == '__main__':
    err_help_msg = "Usage: python app.py [--spotify | --terminal] <port>"
    parser = argparse.ArgumentParser(description='MacOS web commander.')
    parser.add_argument('--spotify', action='store_true', help='Start the Spotify controls')
    parser.add_argument('--terminal', action='store_true', help='Start the app in terminal mode')
    parser.add_argument('port', type=int, nargs='?', help='The port number to run the application on')
    args = parser.parse_args()

    if args.port is None:
        print(err_help_msg)
        sys.exit(1) 

    if args.spotify:
        app.run(debug=True, host='0.0.0.0', port=args.port)
    elif args.terminal:
        print("Terminal mode in develop..")
    else:
        print(err_help_msg)
        sys.exit(1)  

