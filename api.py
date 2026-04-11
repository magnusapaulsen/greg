import os, requests
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

# Load in environment variables
load_dotenv()

def get_secret(key):
    # 1. Look for key in environment variables (local)
    # 2. Look for key in Streamlit secrets (cloud)
    return os.getenv(key) or st.secrets.get(key)

REQUIRED_SECRETS = ['OPENAI_API_KEY', 'IGDB_CLIENT_ID', 'IGDB_CLIENT_SECRET']

def validate_secrets():
    missing = [key for key in REQUIRED_SECRETS if not get_secret(key)]
    if missing:
        st.error(f'Missing required configuration: {", ".join(missing)}. Add them to your .env file or Streamlit secrets.')
        st.stop()

# Cache access token so we don't have to get a new one every time
@st.cache_data(show_spinner=False, ttl=3600)
def get_igdb_token():
    # Get IGDB client ID and IGDB client secret
    client_id = get_secret('IGDB_CLIENT_ID')
    client_secret = get_secret('IGDB_CLIENT_SECRET')

    # POST request to get OAuth2 access token from IGDB
    url = f'https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials'
    try:
        response = requests.post(url, timeout=10)
        response.raise_for_status()
        return response.json().get('access_token')
    except requests.RequestException as e:
        st.error(f'Failed to authenticate with IGDB: {e}')
        return None

@st.cache_data(ttl=86400)
def get_genres():
    token = get_igdb_token()
    if not token:
        return []

    client_id = get_secret('IGDB_CLIENT_ID')
    headers = {'Client-ID': client_id, 'Authorization': f'Bearer {token}'}
    try:
        response = requests.post(
            'https://api.igdb.com/v4/genres',
            headers=headers,
            data='fields name; limit 50; sort name asc;',
            timeout=10
        )
        if response.status_code == 200:
            return [genre['name'] for genre in response.json()]
        return []
    except requests.RequestException:
        return []

@st.cache_data(ttl = 3600)
def search(user_input):

    # Only give suggestions when the user has typed in 2 or more letters
    if not user_input or len(user_input) < 2:
        return []
    
    token = get_igdb_token()
    if not token:
        return []

    client_id = get_secret('IGDB_CLIENT_ID')

    headers = {'Client-ID': client_id, 'Authorization': f'Bearer {token}'}

    data = f'search "{user_input}"; fields name; limit 5;'
    try:
        response = requests.post('https://api.igdb.com/v4/games', headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            return [game['name'] for game in response.json()]
        return []
    except requests.RequestException:
        return []

@st.cache_data(ttl=86400)
def get_game_details(title):
    token = get_igdb_token()
    if not token:
        return None

    client_id = get_secret('IGDB_CLIENT_ID')
    headers = {'Client-ID': client_id, 'Authorization': f'Bearer {token}'}
    try:
        response = requests.post(
            'https://api.igdb.com/v4/games',
            headers=headers,
            data=f'search "{title}"; fields name, summary, cover.url; limit 1;',
            timeout=10
        )
        if response.status_code == 200 and response.json():
            game = response.json()[0]
            cover_url = game.get('cover', {}).get('url')
            if cover_url:
                # Replace thumb size with cover_big for a larger image
                cover_url = 'https:' + cover_url.replace('t_thumb', 't_cover_big')
            return {
                'summary': game.get('summary'),
                'cover_url': cover_url,
            }
        return None
    except requests.RequestException:
        return None

def get_instructions(filename):
    try:
        with open(filename, 'r') as f:
            return f.read()
    except OSError as e:
        st.error(f'Could not load instructions file: {e}')
        return None

def get_recommendation(instructions, user_input):
    try:
        client = OpenAI(api_key=get_secret('OPENAI_API_KEY'))
        return client.responses.create(
            model='gpt-5-nano',
            instructions=instructions,
            input=user_input,
            reasoning={'effort': 'low'}
        )
    except Exception as e:
        st.error(f'Failed to get a recommendation from Greg: {e}')
        return None