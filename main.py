import streamlit as st
from streamlit_searchbox import st_searchbox
import api
import time
from datetime import datetime

def main():
    st.set_page_config(page_title = 'GREG - Game Recommendation Expert, Greg', page_icon = '🤖', layout = 'centered', initial_sidebar_state = 'auto')

    api.validate_secrets()

    # Row 1 - Title
    st.title('GREG', width = 'stretch', text_alignment = 'center')
    st.header('Game Recommendation Expert, Greg', width = 'stretch', text_alignment = 'center')

    # Row 2 - Genre and Mode
    FALLBACK_GENRES = ['Action', 'Action-Adventure', 'Adventure', 'Battle Royale', 'Card Battler', 'Casual', 'Deckbuilder', 'Fighting', 'First-Person Shooter (FPS)', 'Horror', 'Idle', 'Match-3', 'MMORPG', 'MOBA', 'Music/Rhythm', 'Party', 'Platformer', 'Puzzle', 'Racing', 'Role-Playing (RPG)', 'Roguelike', 'Roguelite', 'Sandbox/Open-World', 'Shooter', 'Simulation', 'Souls-like', 'Sports', 'Strategy', 'Survival']
    genres = api.get_genres() or FALLBACK_GENRES
    row_2_column_1, row_2_column_2 = st.columns([1, 1])
    with row_2_column_1:
        genre = st.selectbox('Genre', genres)
    with row_2_column_2:
        mode = st.radio('Mode', options = ['Singleplayer', 'Multiplayer'], horizontal = True)

    st.divider()

    st.subheader('Let Greg know what you like.')
    st.caption('Start typing the name of a game and select it from the dropdown.')
    
    # Row 3 - Game preferences
    row_3_column_1, row_3_column_2 = st.columns([1, 1])
    with row_3_column_1:
        art_game = st_searchbox(api.search, label = 'Art like:', key = 'art_search')
        story_game = st_searchbox(api.search, label = 'Story like:', key = 'story_search')
    with row_3_column_2:
        music_game = st_searchbox(api.search, label = 'Music like:', key = 'music_search')
        gameplay_game = st_searchbox(api.search, label = 'Gameplay like:', key = 'gameplay_search')

    st.divider()

    # Button Row
    if st.button('Ask Greg', type = 'primary', use_container_width = True):
        if not any([art_game, music_game, story_game, gameplay_game]):
            st.warning('Greg is going to need more than that...')
        else:
            # Clear any previous result and start fresh
            st.session_state.pop('result', None)
            st.session_state.pop('balloons_shown', None)

            # Start timer
            start_time = time.time()

            with st.spinner('Greg is thinking...'):
                user_input = (
                    f'Genre: {genre}. Mode: {mode}. '
                    f'Art like: {art_game}. Music like: {music_game}. '
                    f'Story like: {story_game}. Gameplay like: {gameplay_game}.'
                )

                instructions = api.get_instructions('instructions.txt')
                if instructions:
                    cutoff_year = datetime.now().year - 7
                    instructions = instructions.format(cutoff_year=cutoff_year)
                    recommendation = api.get_recommendation(instructions, user_input)
                    if recommendation:
                        end_time = time.time()
                        title = recommendation.output_text
                        details = api.get_game_details(title)
                        st.session_state['result'] = {
                            'title': title,
                            'details': details,
                            'usage': recommendation.usage,
                            'time': round(end_time - start_time, 2),
                        }

    # Render result from session state (persists across rerenders)
    if 'result' in st.session_state:
        result = st.session_state['result']
        details = result.get('details')

        st.write('### 🎯 Greg Recommends:')

        if details and details.get('cover_url'):
            cover_col, text_col = st.columns([1, 3])
            with cover_col:
                st.image(details['cover_url'])
            with text_col:
                st.write(f'## {result["title"]}')
                if details.get('summary'):
                    st.write(details['summary'])
        else:
            st.write(f'## {result["title"]}')

        # Fire balloons only once per new recommendation
        if not st.session_state.get('balloons_shown'):
            st.balloons()
            st.session_state['balloons_shown'] = True

        st.divider()

        # Technical details
        with st.expander("📊 View technical details"):
            usage = result['usage']
            if usage:
                input_tokens = getattr(usage, "input_tokens", 0)
                output_tokens = getattr(usage, "output_tokens", 0)
                total_tokens = getattr(usage, "total_tokens", 0)

                m1, m2, m3, m4 = st.columns(4)
                m1.metric('Input tokens', input_tokens)
                m2.metric('Output tokens', output_tokens)
                m3.metric('Total tokens', total_tokens)
                m4.metric('Time', f'{result["time"]}s')

if __name__ == '__main__':
    main()