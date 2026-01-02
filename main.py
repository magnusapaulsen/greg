import streamlit as st
from streamlit_searchbox import st_searchbox
import api
import time

def main():
    st.set_page_config(page_title = 'GREG - Game Recommendation Expert, Greg', page_icon = '🤖', layout = 'wide', initial_sidebar_state = 'auto')
    
    # Row 1 - Title
    row_1_column_1, row_1_column_2, row_1_column_3 = st.columns([1, 5, 1])
    with row_1_column_2:
        st.title('GREG', width = 'stretch', text_alignment = 'center')
        st.header('Game Recommendation Expert, Greg', width = 'stretch', text_alignment = 'center')

    # Row 2 - Genre and Mode
    row_2_column_1, row_2_column_2 = st.columns([1, 1])
    with row_2_column_1:
        genre = st.selectbox('Genre', ['Action', 'Action-Adventure', 'Adventure', 'Battle Royale', 'Card Battler', 'Casual', 'Deckbuilder', 'Fighting', 'First-Person Shooter (FPS)', 'Horror', 'Idle', 'Match-3', 'MMORPG', 'MOBA', 'Music/Rhythm', 'Party', 'Platformer', 'Puzzle', 'Racing', 'Role-Playing (RPG)', 'Roguelike', 'Roguelite', 'Sandbox/Open-World', 'Shooter', 'Simulation', 'Souls-like', 'Sports', 'Strategy', 'Survival'])
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
    row_4_column_1, row_4_column_2, row_4_column_3 = st.columns([1, 5, 1])
    with row_4_column_2:
        if st.button('Ask Greg', type = 'primary', use_container_width = True):
            if not any([art_game, music_game, story_game, gameplay_game]):
                st.warning('Greg is going to need more than that...')
            else:
                # Start timer
                start_time = time.time()
                
                with st.spinner('Greg is thinking...'):
                    user_input = (
                        f'Genre: {genre}. Mode: {mode}. '
                        f'Art like: {art_game}. Music like: {music_game}. '
                        f'Story like: {story_game}. Gameplay like: {gameplay_game}.'
                    )
                    
                    instructions = api.get_instructions('instructions.txt')
                    recommendation = api.get_recommendation(instructions, user_input)
                    # End timer
                    end_time = time.time()
                    total_time = round(end_time - start_time, 2)

                    # Output
                    st.write('### 🎯 Greg Recommends:')
                    st.write(f'## {recommendation.output_text}')
                    
                    # Balloon-break 🥳
                    st.balloons()

                    st.divider()

                    # Techinal details
                    with st.expander("📊 View technical details"):
                        usage = getattr(recommendation, "usage", None)
                                        
                        if usage:
                            input_tokens = getattr(usage, "input_tokens", 0)
                            output_tokens = getattr(usage, "output_tokens", 0)
                            total_tokens = getattr(usage, "total_tokens", 0)
                                            
                            m1, m2, m3, m4 = st.columns(4)
                            m1.metric('Input tokens', input_tokens)
                            m2.metric('Output tokens', output_tokens)
                            m3.metric('Total tokens', total_tokens)
                            m4.metric('Time', f'{total_time}s')

if __name__ == '__main__':
    main()