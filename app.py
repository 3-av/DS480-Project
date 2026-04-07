import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import requests
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="DS450 Project", page_icon="🎵", layout="centered")

st.markdown("""
    <style>
    /* Hides the default 'Press Enter to submit form' text */
    div[data-testid="InputInstructions"] { display: none; }
    </style>
""", unsafe_allow_html=True)

client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

if not client_id or not client_secret:
    st.error("Spotify credentials not found. Please check your .env file.")
    st.stop()

sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(client_id=client_id, client_secret=client_secret))

if 'dataset' not in st.session_state: st.session_state.dataset = []
if 'search_results' not in st.session_state: st.session_state.search_results = []

def add_track(track_data):
    st.session_state.dataset.append(track_data)
    # Removed clearing search_results to allow multiple additions

st.title("Track Selector")

with st.form("search_form", border=False):
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input("Search for a track:", label_visibility="collapsed", placeholder="Type a song and press Enter to search")
    with col2:
        submitted = st.form_submit_button("Search", use_container_width=True)

    if submitted and query:
        with st.spinner("Searching"):
            try:
                results = sp.search(q=query, type='track', limit=5)
                st.session_state.search_results = results['tracks']['items']
            except Exception as e:
                st.error(f"An error occurred during search: {e}")
                st.session_state.search_results = []

if st.session_state.search_results:
    st.write("### Results:")
    
    cols = st.columns(5)
    
    for i, track in enumerate(st.session_state.search_results):
        with cols[i]:
            with st.container(border=True):
                cover_url = track['album']['images'][1]['url'] if len(track['album']['images']) > 1 else "https://via.placeholder.com/150"
                st.image(cover_url, use_container_width=True)
                
                title = track['name']
                artist = track['artists'][0]['name']
            
                display_title = title if len(title) < 35 else title[:32] + "..."                
                st.markdown(f"""
                    <div style="height: 85px;">
                        <div style="font-weight: bold; margin-bottom: 4px; line-height: 1.2;">{display_title}</div>
                        <div style="color: gray; font-size: 0.85em;">{artist}</div>
                    </div>
                """, unsafe_allow_html=True)
                
                track_data = {
                    'Title': title,
                    'Artist': artist,
                    'Popularity': track['popularity'],
                    'Duration_MS': track['duration_ms'],
                    'Explicit': 'Yes' if track['explicit'] else 'No',
                    'Release_Date': track['album']['release_date']
                }
                
                st.button("Add", key=track['id'], use_container_width=True, on_click=add_track, args=(track_data,))

if st.session_state.dataset:
    st.divider()
    
    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        st.write(f"### Current Dataset ({len(st.session_state.dataset)} tracks)")
        
    df = pd.DataFrame(st.session_state.dataset)
    
    with head_col2:
        st.download_button(
            label="Export to CSV", 
            data=df.to_csv(index=False).encode('utf-8'), 
            file_name='ds450_spotify_data.csv', 
            mime='text/csv', 
            use_container_width=True
        )
        
    st.dataframe(df, use_container_width=True, hide_index=True)