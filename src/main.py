from flask import Flask, render_template, jsonify, request, session, redirect, url_for
from datetime import datetime
import platform
import os
import sys
import json
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-change-me")

# OAuth setup
oauth = OAuth(app)
# Try to load credentials from google_oauth.json if it exists (downloaded from Google Cloud)
cred_path = os.path.join(os.path.dirname(__file__), '..', 'google_oauth.json')
if os.path.exists(cred_path):
    try:
        with open(cred_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            web = data.get('web') or data.get('installed') or {}
            GOOGLE_CLIENT_ID = web.get('client_id')
            GOOGLE_CLIENT_SECRET = web.get('client_secret')
    except Exception:
        GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
        GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')
else:
    GOOGLE_CLIENT_ID = os.getenv('GOOGLE_CLIENT_ID')
    GOOGLE_CLIENT_SECRET = os.getenv('GOOGLE_CLIENT_SECRET')

oauth.register(
    name='google',
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    # Use OpenID Connect discovery so Authlib can obtain jwks_uri and other endpoints
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login')
def login():
    # Build absolute HTTPS redirect URI for Google
    redirect_uri = url_for('auth', _external=True, _scheme='https')
    return oauth.google.authorize_redirect(redirect_uri)


@app.route('/auth')
def auth():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.get('userinfo').json()
    session['user'] = {
        'id': user_info.get('id'),
        'email': user_info.get('email'),
        'name': user_info.get('name'),
        'picture': user_info.get('picture'),
    }
    return redirect(url_for('profile'))


@app.route('/profile')
def profile():
    user = session.get('user')
    if not user:
        return redirect(url_for('home'))
    return render_template('profile.html', user=user)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

@app.route('/get_message')
def get_message():
    # Get current timestamp in different formats
    current_time = datetime.now()
    
    # Create a complex JSON structure
    server_data = {
        "message": "Hello from the server! This message came through AJAX!",
        "timestamp": {
            "full": current_time.strftime("%Y-%m-%d %H:%M:%S"),
            "date": current_time.strftime("%Y-%m-%d"),
            "time": current_time.strftime("%H:%M:%S"),
            "unix": int(current_time.timestamp())
        },
        "server_info": {
            "platform": platform.system(),
            "python_version": platform.python_version(),
            "processor": platform.processor(),
            "machine": platform.machine()
        },
        "request_data": {
            "method": request.method,
            "path": request.path,
            "user_agent": request.headers.get('User-Agent'),
            "ip_address": request.remote_addr,
            "headers": dict(request.headers)
        },
        "environment": {
            "working_directory": os.getcwd(),
            "temp_directory": os.getenv('TEMP', 'Not Available'),
            "python_path": sys.executable
        }
    }
    
    return jsonify(server_data)

if __name__ == "__main__":
    # Run with a self-signed (adhoc) certificate for local development by default.
    # Note: browsers will warn about the certificate; accept the exception for testing.
    # On some systems you may need pyOpenSSL/cryptography in the venv: pip install pyopenssl cryptography
    app.run(debug=True, host="0.0.0.0", port=5000, ssl_context='adhoc')
