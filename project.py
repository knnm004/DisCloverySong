import streamlit as st
import pylast
import time
import pandas as pd
import plotly.express as px
import random
import os
import csv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# --- CONFIGURATION ---
API_KEY = "YOUR-API-KEY"
USER_AGENT = "DisCloverySong/1.0"

# Connect to Last.fm
network = pylast.LastFMNetwork(api_key=API_KEY)

TOP_TAGS = ["rock", "electronic", "alternative", "pop", "indie", "metal", "jazz", "classic rock", "ambient", "experimental", "folk", "punk", "Hip-Hop", "hard rock", "instrumental", "singer-songwriter", "dance", "80s", "soul", "chillout", "techno", "new wave"]

class VibeMapper:
    def __init__(self, tag_list):
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        self.vector_db = FAISS.from_texts(tag_list, self.embeddings)

    def find_best_tag(self, user_query):
        results = self.vector_db.similarity_search(user_query, k=1)
        return results[0].page_content if results else None

if "tag_mapper" not in st.session_state:
    st.session_state.tag_mapper = VibeMapper(TOP_TAGS)

# --- HELPER FUNCTIONS ---
def get_random_song():
    top_tracks = network.get_top_tracks(limit=50)
    return random.choice(top_tracks).item

def search_by_vibe(vibe_text):
    mapped_tag_name = st.session_state.tag_mapper.find_best_tag(vibe_text)
    tag = network.get_tag(mapped_tag_name)
    tracks = tag.get_top_tracks(limit=40)
    
    if tracks:
        selected_item = random.choice(tracks)
        track = selected_item.item
        listeners = track.get_listener_count()
        return track, mapped_tag_name, int(listeners)
    return None, mapped_tag_name, 0

def save_listening_data(track, listener_count, liked=False):
    playcount = track.get_playcount()
    new_data = {
        "Timestamp": [time.strftime("%Y-%m-%d %H:%M:%S")],
        "Artist": [track.artist.name],
        "Title": [track.title],
        "Play_Count": [playcount],
        "Listeners": [listener_count],
        "Liked": [liked]
    }
    df = pd.DataFrame(new_data)
    file_path = "history.csv"
    file_exists = os.path.exists(file_path)
    df.to_csv(file_path, mode='a', header=not file_exists, index=False, quoting=csv.QUOTE_NONNUMERIC)

# --- STREAMLIT UI ---
st.set_page_config(page_title="DisCloverySong", page_icon="🎵🍀")
st.title("🎵 DisCloverySong 🍀")
st.caption("The app that rediscovers the art of listening.")

# Sidebar
with st.sidebar:
    st.header("Discovery Settings")
    mode = st.radio("Choose Mode", ["Random", "Scope (Vibe)"])
    
    if mode == "Scope (Vibe)":
        query = st.text_input("Describe the vibe:", placeholder="e.g. dreamy, techno, sad")
    
    if st.button("Generate Discovery"):
        with st.spinner("Finding your song..."):
            if mode == "Random":
                st.session_state.current_track = get_random_song()
                st.session_state.mapped_tag = "Random"
                st.session_state.current_listeners = 0
            else:
                track, tag_used, listeners = search_by_vibe(query)
                st.session_state.current_track = track
                st.session_state.mapped_tag = tag_used
                st.session_state.current_listeners = listeners
            
            # Reset states for new song
            st.session_state.listening_finished = False
            st.rerun()

# --- PLAYER SECTION ---
if "current_track" in st.session_state and st.session_state.current_track:
    track = st.session_state.current_track
    
    st.subheader(f"Now Listening: {track.title} by {track.artist.name}")
    st.markdown(f"**Mapped Vibe:** `{st.session_state.get('mapped_tag', 'N/A')}`")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        try:
            cover_url = track.get_cover_image(3) # 3 is Extra Large
            if cover_url:
                st.image(cover_url, use_container_width=True)
            else:
                st.info("No album art found.")
        except:
            st.error("Image load failed.")

    with col2:
        raw_dur = track.get_duration() 
        duration = raw_dur / 1000 if raw_dur else 180
        m, s = divmod(int(duration), 60)
        
        st.write(f"⏱️ **Duration:** {m}:{s:02d}")
        st.write(f"👥 **Listeners:** {st.session_state.get('current_listeners', 0):,}")
        
        search_q = f"{track.artist.name} {track.title}".replace(" ", "+")
        st.link_button("▶️ Listen on YouTube", f"https://www.youtube.com/results?search_query={search_q}")

    st.divider()

    # Listening logic
    if not st.session_state.get("listening_finished", False):
        if st.button("I am ready to listen (No skipping allowed)"):
            bar = st.progress(0)
            status = st.empty()
            step = duration / 100
            for p in range(100):
                time.sleep(step)
                bar.progress(p + 1)
                status.text(f"Listening... {p + 1}%")
            st.session_state.listening_finished = True
            st.rerun()
    
    # Post-listening logic
    else:
        st.success("✅ Song Complete!")
        is_liked = st.toggle("❤️ I love this discovery!", value=False)
        
        if st.button("🚀 Log to Journey & Save"):
            save_listening_data(
                st.session_state.current_track, 
                st.session_state.get("current_listeners", 0), 
                liked=is_liked
            )
            st.balloons()
            st.session_state.current_track = None
            st.session_state.listening_finished = False
            st.rerun()
else:
    st.info("Choose a mode in the sidebar to start.")

# --- VISUALIZATION ---
st.divider()
if st.checkbox("Show My Listening History"):
    if os.path.exists("history.csv"):
        history_df = pd.read_csv("history.csv")
        # Ensure Liked is string for distinct symbol mapping
        history_df["Liked"] = history_df["Liked"].astype(str)
        
        fig = px.scatter(
            history_df, x="Play_Count", y="Listeners",
            hover_name="Title", color="Artist",
            symbol="Liked", symbol_map={"True": "star", "False": "circle"},
            title="Discovery Map",
            labels={"Play_Count": "Global Plays", "Listeners": "Unique Listeners"}
        )

        for trace in fig.data:
            if "True" in trace.name or "False" in trace.name:
                trace.showlegend = False

        fig.update_traces(marker=dict(size=14))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No history found. Listen to the songs then see your data! :D")