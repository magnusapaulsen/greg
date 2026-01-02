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

# Cache access token so we don't have to get a new one every time
@st.cache_data(show_spinner=False)
def get_igdb_token():
    # Get IGDB client ID and IGDB client cecret
    client_id = get_secret('IGDB_CLIENT_ID')
    client_secret = get_secret('IGDB_CLIENT_SECRET')

    # POST request to get OAuth2 access token from IGDB
    url = f'https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials'
    # Try/Except here
    response = requests.post(url)
    return response.json().get('access_token')

@st.cache_data(ttl = 3600)
def search(user_input):

    # Only give suggestions when the user has typed in 2 or more letters
    if not user_input or len(user_input) < 2:
        return []
    
    token = get_igdb_token()
    client_id = get_secret('IGDB_CLIENT_ID')

    headers = {'Client-ID': client_id, 'Authorization': f'Bearer {token}'}

    data = f'search "{user_input}"; fields name; limit 5;'
    response = requests.post('https://api.igdb.com/v4/games', headers = headers, data = data)

    if response.status_code == 200:
        return [game['name'] for game in response.json()]
    else:
        return []

def get_instructions(filename):
    with open(filename, 'r') as f:
        return f.read()

def get_recommendation(instructions, user_input):
    client = OpenAI(api_key=get_secret('OPENAI_API_KEY'))

    return client.responses.create(
        model = 'gpt-5-nano',
        instructions = instructions,
        input = user_input,
        reasoning = {'effort': 'low'}
    )