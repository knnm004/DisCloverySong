# 🎵 DisCloverySong 🍀
The app that rediscovers the art of listening.

**DisCloverySong** is a music discovery platform built with Streamlit that challenges the modern "skip-culture" of music streaming. By combining AI-powered vibe mapping with a mandatory "No-Skip" listening challenge, it encourages users to fully immerse themselves in new tracks before logging them to a personalized discovery map.



![alt](https://github.com/knnm004/streamlit/blob/main/asset/DisCloverySong.jpg)

## Features
**Vibe-to-Tag Mapping**: Uses LangChain and HuggingFace embeddings to translate natural language "vibes" (e.g., "dreamy afternoon," "industrial techno") into the most relevant Last.fm genre tags.

**No-Skip Challenge**: A progress-locked player that forces users to listen to a song for its actual duration before it can be saved to their history.

**Interactive Discovery Map**: A Plotly-powered scatter plot that visualizes your journey based on Global Plays (Mass Appeal) vs. Unique Listeners (Reach).

**Personal Favorites**: A "Like" feature that marks specific discoveries with a Star symbol on your map.

**Rich Metadata**: Automatically fetches high-quality album art and real-time community statistics directly from the Last.fm API.

##  Getting Started
**1. Prerequisites**
Python 3.8 or higher.

A Last.fm API Key (available at last.fm/api).

**2. Installation**
Clone the repository:

```Bash

git clone https://github.com/knnm004/streamlit.git
cd streamlit
Install the required Python libraries: pip install streamlit pylast pandas plotly langchain langchain-community langchain-huggingface faiss-cpu sentence-transformers
````
```Bash

pip install streamlit pylast pandas plotly langchain langchain-community langchain-huggingface faiss-cpu sentence-transformers
````
**3. Configuration**
Replace the API_KEY in project.py with your personal Last.fm API key:

```Python

API_KEY = "YOUR_LASTFM_API_KEY_HERE"
````
**4. Usage**
Launch the application:

```Bash

streamlit run project.py
````
You can discover new songs by either geting from the *shuffle* or *typing the vibe to scope*

![alt](https://github.com/knnm004/streamlit/blob/main/asset/DisCloverySong_Shuffle.jpg)



![alt](https://github.com/knnm004/streamlit/blob/main/asset/DisCloverySong_Listening.jpg)

## The Discovery Map
The app categorizes your music discoveries using two primary metrics from the Last.fm community:

**X-Axis (Play Count)**: Total global plays. High values indicate mainstream hits; low values indicate underground tracks.

**Y-Axis (Listeners)**: Total unique listeners. This represents the "Reach" of an artist.

**Star Symbol**: Tracks you "Liked" during the No-Skip challenge.

**Circle Symbol**: Tracks you listened to but did not mark as a favorite.


![alt](https://github.com/knnm004/streamlit/blob/main/asset/DisCloverySong_DiscoveryMap.jpg)

# File Structure
```text
streamlit/
├── .streamlit/
│   └── config.toml          # Custom Streamlit theme and server settings
├── data/
│   └── history.csv          # Local storage for your listening journey
├── src/
│   ├── __init__.py
│   ├── vibe_mapper.py       # VibeMapper class and AI logic
│   └── utils.py             # Last.fm and CSV helper functions
├── project.py               # Main application entry point (Streamlit UI)
├── requirements.txt         # List of Python dependencies
├── README.md                # Project documentation and guide
└── .gitignore               # Files to exclude from Git (like history.csv)
