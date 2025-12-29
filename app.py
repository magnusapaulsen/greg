import os
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

# API Key and OpenAI Client
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_instructions(filename):
    with open(filename, 'r') as f:
        return f.read()

def get_recommendation(instructions, user_input):
    return client.responses.create(
        model = 'gpt-5-nano',
        instructions = instructions,
        input = user_input,
        reasoning = {'effort': 'medium'}
    )

def main():
    # Title
    st.title('GREG')
    st.header('Game Recommendation Expert, Greg')
    st.subheader('Ask, and you shall receive, inshallah!')
    
    # Form
    with st.form(key = 'form_key', clear_on_submit = True):
        genre = st.text_input("What genre do you want?", placeholder="e.g., RPG, Action")
        mode = st.radio('Mode', options = ['Singleplayer', 'Multiplayer'], horizontal = True)
        art = st.text_input("Art like:", placeholder="e.g., Cyberpunk 2077")
        music = st.text_input("Music like:", placeholder="e.g., Witcher 3")
        story = st.text_input("Story like:", placeholder="e.g., Mass Effect 2")
        gameplay = st.text_input("Gameplay like:", placeholder="e.g., Elden Ring")

        submitted = st.form_submit_button(label = 'Ask GREG', type = 'primary')
    
    # Form submitted
    if submitted:
        # User input
        user_input = (
            f'Genre: {genre}. '
            f'Mode: {mode}. '
            f'Art like: {art}. '
            f'Music like: {music}. '
            f'Story like: {story}. '
            f'Gameplay like: {gameplay}'
        )
        # Ask GREG
        recommendation = get_recommendation(get_instructions('instructions.txt'), user_input)

        st.success(f"# **{recommendation.output_text}**")
        st.write(recommendation.usage.total_tokens)
        st.balloons()

        if hasattr(recommendation, "usage"):
            print("Tokens used:", recommendation.usage.total_tokens)

if __name__ == '__main__':
    main()