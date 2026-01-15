import streamlit as st
import pylast
import time
import pandas as pd
import plotly.express as px
import random
from langchain.agents import create_agent
from langchain.tools import tool

# --- CONFIGURATION ---
API_KEY = "47b5c5c8f34a00a3c4dbef927f9cd2db"
USER_AGENT = "DisCloverySong/1.0"

# Connect to Last.fm (Public access only)
network = pylast.LastFMNetwork(api_key=API_KEY)

# --- HELPER FUNCTIONS ---
def get_random_song():
    """Fetches a random track from the global top chart."""
    top_tracks = network.get_top_tracks(limit=50)
    return random.choice(top_tracks).item

def search_by_vibe(vibe_text):
    """Searches for tracks matching a specific tag/vibe."""
    # Last.fm works best with single tags (e.g., 'dreamy', 'rock')
    tag = network.get_tag(vibe_text)
    tracks = tag.get_top_tracks(limit=10)
    if tracks:
        return random.choice(tracks).item
    return None

def save_listening_data(track):
    """Saves metadata to a CSV for visualization."""
    new_data = {
        "Timestamp": [time.strftime("%Y-%m-%d %H:%M:%S")],
        "Artist": [track.artist.name],
        "Title": [track.title],
        "Vibe_Score": [random.uniform(0, 1)] # Placeholder for Valence แก้แก้
    }
    df = pd.DataFrame(new_data)
    df.to_csv("history.csv", mode='a', header=not pd.io.common.file_exists("history.csv"), index=False)

# --- STREAMLIT UI ---
st.set_page_config(page_title="DisCloverySong", page_icon="🎵")
st.title("🎵 DisCloverySong")
st.caption("The app that rediscovers the art of listening.")

# Sidebar for Discovery
with st.sidebar:
    st.header("Discovery Settings")
    mode = st.radio("Choose Mode", ["Random", "Scope (Vibe)"])
    
    if mode == "Scope (Vibe)":
        query = st.text_input("Describe the vibe:", placeholder="e.g. dreamy, techno, sad")
    
    if st.button("Generate Discovery"):
        with st.spinner("Finding your song..."):
            if mode == "Random":
                st.session_state.current_track = get_random_song()
            else:
                st.session_state.current_track = search_by_vibe(query)
            st.session_state.play_start = False

# --- PLAYER SECTION ---
if "current_track" in st.session_state and st.session_state.current_track:
    track = st.session_state.current_track
    st.subheader(f"Now Listening: {track.title} by {track.artist.name}")
    
    # YouTube Search Link (Helper for the user to find the audio)
    yt_url = f"https://www.youtube.com/results?search_query={track.artist.name}+{track.title}".replace(" ", "+")
    st.markdown(f"[Click here to open song in YouTube]({yt_url})")
    
    # THE "NO-SKIP" CHALLENGE
    # Since we can't lock the YouTube browser tab, we lock the app's progress.
    duration = 180  # Assume 3 minutes if duration is unavailable
    
    if not st.session_state.get("play_start", False):
        if st.button("I am ready to listen (No skipping allowed)"):
            st.session_state.play_start = True
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for percent in range(100):
                time.sleep(duration / 100) # Simulate song duration
                progress_bar.progress(percent + 1)
                status_text.text(f"Listening... {percent + 1}% complete")
            
            st.success("✅ Song Complete! Data logged to your journey.")
            save_listening_data(track)
else:
    st.info("Choose a mode in the sidebar to start your discovery.")

# --- DATA VISUALIZATION ---
st.divider()
if st.checkbox("Show My Listening History"):
    try:
        history_df = pd.read_csv("history.csv")
        st.write("### Your Discovery Map")
        fig = px.scatter(history_df, x="Timestamp", y="Vibe_Score", 
                         hover_name="Title", color="Artist",
                         title="Listening Journey Over Time")
        st.plotly_chart(fig)
    except FileNotFoundError:
        st.warning("No listening history found yet. Finish a song to see data!")