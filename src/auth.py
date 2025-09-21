from flask import Blueprint, session, redirect, url_for, render_template
from authlib.integrations.flask_client import OAuth
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from dotenv import load_dotenv
import os
import json

auth_bp = Blueprint('auth', __name__)

oauth = None
login_manager = LoginManager()


class User(UserMixin):
    def __init__(self, id_, name, email, picture):
        self.id = id_
        self.name = name
        self.email = email
        self.picture = picture


@login_manager.user_loader
def load_user(user_id):
    user = session.get('user')
    if user and str(user.get('id')) == str(user_id):
        return User(user.get('id'), user.get('name'), user.get('email'), user.get('picture'))
    return None


def init_app(app):
    """Initialize OAuth and Flask-Login and register the auth blueprint."""
    global oauth
    load_dotenv()
    # Ensure app has a secret key; don't override if already set by main
    if not app.secret_key:
        app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-change-me')

    oauth = OAuth(app)

    # Try to load credentials from google_oauth.json in project root
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
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid email profile'},
    )

    login_manager.init_app(app)
    app.register_blueprint(auth_bp)


@auth_bp.route('/login')
def login():
    # Build absolute HTTPS redirect URI for Google
    redirect_uri = url_for('auth.auth', _external=True, _scheme='https')
    return oauth.google.authorize_redirect(redirect_uri)


@auth_bp.route('/auth')
def auth():
    token = oauth.google.authorize_access_token()
    user_info = oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo').json()
    session['user'] = {
        'id': user_info.get('id'),
        'email': user_info.get('email'),
        'name': user_info.get('name'),
        'picture': user_info.get('picture'),
    }
    user_obj = User(user_info.get('id'), user_info.get('name'), user_info.get('email'), user_info.get('picture'))
    login_user(user_obj)
    return redirect(url_for('auth.profile'))


@auth_bp.route('/profile')
@login_required
def profile():
    # current_user provided by Flask-Login
    return render_template('profile.html')


@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    logout_user()
    return redirect(url_for('auth.home') if hasattr(url_for, 'home') else '/')
