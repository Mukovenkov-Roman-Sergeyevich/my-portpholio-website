from flask import render_template, redirect, session, url_for, flash, request
from app import app, db, Like
import os
import requests

@app.route('/')
def home():
    user_name = 'Гость'
    if 'user_name' in session:
        user_name = session['user_name']

    return render_template('index.html', user_name=user_name)

@app.route('/skills')
def skills():
    user_name = 'Гость'
    has_liked = False

    if 'user_name' in session:
        user_name = session['user_name']

    likes = Like.query.filter_by(page='skills').count()

    if (user_name != "Гость"):
        has_liked = Like.query.filter_by(page='skills', user_email=session['user_email']).first() is not None

    return render_template('skills.html', user_name=user_name, likes=likes, has_liked=has_liked)

@app.route('/projects')
def projects():
    user_name = 'Гость'
    has_liked1 = has_liked2 = has_liked3 = False

    if 'user_name' in session:
        user_name = session['user_name']

    likes_project1 = Like.query.filter_by(page='project1').count()
    likes_project2 = Like.query.filter_by(page='project2').count()
    likes_project3 = Like.query.filter_by(page='project3').count()

    if ('user_email' in session):
        has_liked1 = Like.query.filter_by(page='project1', user_email=session['user_email']).first() is not None
        has_liked2 = Like.query.filter_by(page='project2', user_email=session['user_email']).first() is not None
        has_liked3 = Like.query.filter_by(page='project3', user_email=session['user_email']).first() is not None

    return render_template('projects.html', user_name=user_name,
                           likes_project1=likes_project1,
                           likes_project2=likes_project2,
                           likes_project3=likes_project3,
                           has_liked1=has_liked1,
                           has_liked2=has_liked2,
                           has_liked3=has_liked3)


@app.route('/toggle_like', methods=['POST'])
def toggle_like():
    page = request.form.get('page')

    # Check if user is logged in with Google or GitHub
    if 'user_email' not in session:
        flash('You are not authorized! Please log in.', 'danger')
        return redirect(url_for('index'))  # Redirect to index or login page

    # Retrieve user details from session
    user_email = session['user_email']

    # Check if the user has already liked the page
    existing_like = Like.query.filter_by(page=page, user_email=user_email).first()

    if existing_like:
        db.session.delete(existing_like)
        flash('You unliked the page!', 'success')
    else:
        new_like = Like(page=page, user_email=user_email)
        db.session.add(new_like)
        flash('You liked the page!', 'success')

    db.session.commit()

    # Redirect based on the page parameter
    if page == 'skills':
        return redirect(url_for('skills'))
    elif page in ['project1', 'project2', 'project3']:
        return redirect(url_for('projects'))
    else:
        return redirect(url_for('home'))

# Google OAuth flow: Step 1 - Redirect to Google login
@app.route('/google/login')
def google_login():
    google_oauth_url = 'https://accounts.google.com/o/oauth2/v2/auth'
    client_id = app.config['GOOGLE_CLIENT_ID']
    redirect_uri = app.config['GOOGLE_REDIRECT_URI']
    scope = 'https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email'
    response_type = 'code'
    state = os.urandom(24).hex()  # Secure random string for CSRF protection

    # Save the state in session to validate on return
    session['state'] = state

    # Construct Google OAuth URL
    auth_url = f"{google_oauth_url}?client_id={client_id}&redirect_uri={redirect_uri}&scope={scope}&response_type={response_type}&state={state}"
    return redirect(auth_url)

# Google OAuth callback: Step 2 - Exchange code for token
@app.route('/google/authorized')
def google_authorized():
    # Check if the state matches (to prevent CSRF attacks)
    if request.args.get('state') != session.get('state'):
        return "State mismatch error.", 400

    # Get the authorization code from the query params
    code = request.args.get('code')

    if not code:
        return "No code in request", 400

    # Google API token endpoint
    google_token_url = 'https://oauth2.googleapis.com/token'

    # Prepare data to exchange code for access token
    data = {
        'code': code,
        'client_id': app.config['GOOGLE_CLIENT_ID'],
        'client_secret': app.config['GOOGLE_CLIENT_SECRET'],
        'redirect_uri': app.config['GOOGLE_REDIRECT_URI'],
        'grant_type': 'authorization_code'
    }

    # Make the request to exchange code for an access token
    response = requests.post(google_token_url, data=data)
    if response.status_code != 200:
        return "Error fetching token from Google", 400

    # Extract the token from response
    token_data = response.json()
    access_token = token_data.get('access_token')
    if not access_token:
        return "No access token returned from Google", 400

    # Save the access token in the session
    session['google_access_token'] = access_token

    # Fetch user info from Google
    user_info = get_google_user_info(access_token)
    session['user_name'] = user_info.get('name', 'No Name')  # Use get() to avoid KeyError
    session['user_email'] = user_info.get('email', 'No Email')

    return redirect(url_for('home'))  # Redirect to the home page

def get_google_user_info(access_token):
    google_user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(google_user_info_url, headers=headers)
    if response.status_code != 200:
        return None
    return response.json()

# GitHub OAuth flow: Step 1 - Redirect to GitHub login
@app.route('/github/login')
def github_login():
    github_oauth_url = 'https://github.com/login/oauth/authorize'
    client_id = app.config['GITHUB_CLIENT_ID']
    redirect_uri = app.config['GITHUB_REDIRECT_URI']
    state = os.urandom(24).hex()  # CSRF protection

    # Save the state in session to validate on return
    session['state'] = state

    # Construct GitHub OAuth URL
    auth_url = f"{github_oauth_url}?client_id={client_id}&redirect_uri={redirect_uri}&state={state}"
    return redirect(auth_url)

# GitHub OAuth callback: Step 2 - Exchange code for token
@app.route('/github/authorized')
def github_authorized():
    # Check if the state matches (to prevent CSRF attacks)
    if request.args.get('state') != session.get('state'):
        return "State mismatch error.", 400

    # Get the authorization code from the query params
    code = request.args.get('code')

    if not code:
        return "No code in request", 400

    # GitHub API token endpoint
    github_token_url = 'https://github.com/login/oauth/access_token'

    # Prepare data to exchange code for access token
    data = {
        'code': code,
        'client_id': app.config['GITHUB_CLIENT_ID'],
        'client_secret': app.config['GITHUB_CLIENT_SECRET'],
        'redirect_uri': app.config['GITHUB_REDIRECT_URI'],
        'state': session.get('state')
    }

    # Make the request to exchange code for an access token
    response = requests.post(github_token_url, data=data, headers={'Accept': 'application/json'})
    if response.status_code != 200:
        return "Error fetching token from GitHub", 400

    # Extract the token from response
    token_data = response.json()
    access_token = token_data.get('access_token')
    if not access_token:
        return "No access token returned from GitHub", 400

    # Save the access token in the session
    session['github_access_token'] = access_token

    # Fetch user info from GitHub
    user_info = get_github_user_info(access_token)
    session['github_user_info'] = user_info
    session['user_name'] = user_info['login']
    session['user_email'] = user_info['email']

    return redirect(url_for('home'))  # Redirect to the home page


# Fetch user info from GitHub API
def get_github_user_info(access_token):
    github_user_info_url = 'https://api.github.com/user'
    headers = {'Authorization': f'token {access_token}'}
    response = requests.get(github_user_info_url, headers=headers)
    if response.status_code != 200:
        return None
    return response.json()