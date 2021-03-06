from flask import request, url_for, session
from flask_login import login_user, logout_user
from requests_oauthlib import OAuth2Session
from werkzeug.utils import redirect
from app import app
from app.auth.models import User


@app.route('/login')
def login():
    client_id = app.config['OAUTH_CLIENT_ID']
    client_secret = app.config['OAUTH_CLIENT_SECRET']
    token_url = app.config['OAUTH_TOKEN_URL']
    redirect_url = app.config['OAUTH_REDIRECT_URL']

    if redirect_url is None:
        redirect_url = url_for('index', _external=True)

    oauth2_session = OAuth2Session(client_id, scope=[], redirect_uri=redirect_url + 'login')
    oauth2_session.fetch_token(token_url, client_secret=client_secret, authorization_response=request.url)

    authenticate_user(oauth2_session)

    return redirect(redirect_url)


@app.route('/logout')
def logout():
    logout_url = app.config['OAUTH_LOGOUT_URL']
    redirect_url = app.config['OAUTH_REDIRECT_URL']
    logout_user()

    if redirect_url is None:
        redirect_url = url_for('index', _external=True)

    logout_url = logout_url + '?redirect_uri=' + redirect_url
    return redirect(logout_url)


def authenticate_user(oauth2_session):
    user_json = oauth2_session.get(app.config['OAUTH_USER_URL']).json()
    app.logger.debug("Authenticating user: " + str(user_json))
    name = user_json.get('name', '').encode('utf-8')
    surname = user_json.get('surnames', '').encode('utf-8')
    user = User(user_json.get('email'), name + ' ' + surname, user_json.get('picture'))
    login_user(user)
    session['user'] = dict(email=user.username, name=user.name, picture=user.picture)
