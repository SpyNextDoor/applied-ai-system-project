"""
Streamlit web interface for the Music Recommender Simulation.

Reuses the same recommend_songs / generate_explanation pipeline as main.py,
just with a browser UI instead of printed CLI output.
"""

import os

import streamlit as st

from recommender import load_songs, recommend_songs
from retrieval import KnowledgeBase
from explain import generate_explanation

SONGS_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "songs.csv")

PRESET_PROFILES = {
    "Custom": None,
    "High-Energy Pop": {
        "genre": "pop", "mood": "happy", "energy": 0.9, "valence": 0.85,
        "danceability": 0.9, "acousticness": 0.1, "tempo": 128,
    },
    "Chill Lofi": {
        "genre": "lofi", "mood": "relaxed", "energy": 0.2, "valence": 0.5,
        "danceability": 0.3, "acousticness": 0.7, "tempo": 75,
    },
    "Deep Intense Rock": {
        "genre": "rock", "mood": "intense", "energy": 0.95, "valence": 0.4,
        "danceability": 0.4, "acousticness": 0.05, "tempo": 150,
    },
}


@st.cache_resource
def get_knowledge_base() -> KnowledgeBase:
    return KnowledgeBase()


@st.cache_data
def get_songs():
    return load_songs(SONGS_DATA_DIR)


@st.cache_data
def get_genres_and_moods():
    songs = get_songs()
    genres = sorted({s["genre"] for s in songs if s.get("genre")})
    moods = sorted({s["mood"] for s in songs if s.get("mood")})
    return genres, moods


CUSTOM_CSS = """
<style>
.stApp {
    background: linear-gradient(180deg, #1a1033 0%, #130c26 55%, #0d0818 100%);
}
h1 {
    font-weight: 800 !important;
    background: linear-gradient(90deg, #ff6ec7, #7f5aff, #4fd0e9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
[data-testid="stCaptionContainer"] {
    color: #b9aedd !important;
}
div[data-testid="stForm"] {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 18px;
    padding: 1.5rem 1.5rem 0.5rem 1.5rem;
    backdrop-filter: blur(6px);
}
div[data-testid="stFormSubmitButton"] button {
    width: 100%;
    border-radius: 12px;
    border: none;
    background: linear-gradient(90deg, #ff6ec7, #7f5aff);
    color: white;
    font-weight: 700;
    padding: 0.6rem 0;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}
div[data-testid="stFormSubmitButton"] button:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 18px rgba(127, 90, 255, 0.45);
}
div[data-testid="stContainer"] {
    background: rgba(255, 255, 255, 0.045);
    border: 1px solid rgba(255, 255, 255, 0.09) !important;
    border-radius: 16px !important;
    transition: border-color 0.15s ease;
}
div[data-testid="stContainer"]:hover {
    border-color: rgba(127, 90, 255, 0.5) !important;
}
div[data-testid="stExpander"] {
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.08);
}
.song-rank-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 1.8rem;
    height: 1.8rem;
    border-radius: 50%;
    background: linear-gradient(135deg, #ff6ec7, #7f5aff);
    color: white;
    font-weight: 700;
    font-size: 0.85rem;
    margin-right: 0.5rem;
}
.song-title {
    font-size: 1.1rem;
    font-weight: 700;
}
.song-artist {
    color: #b9aedd;
    font-weight: 400;
}
.explanation-box {
    border-left: 3px solid #7f5aff;
    padding: 0.5rem 0.9rem;
    margin-top: 0.6rem;
    background: rgba(127, 90, 255, 0.08);
    border-radius: 0 10px 10px 0;
}
.tag-pill {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    padding: 0.12rem 0.55rem;
    border-radius: 999px;
    margin-bottom: 0.3rem;
}
.tag-llm {
    background: rgba(79, 208, 233, 0.18);
    color: #4fd0e9;
}
.tag-fallback {
    background: rgba(255, 255, 255, 0.12);
    color: #d6cdf5;
}
.tag-ungrounded {
    background: rgba(255, 110, 199, 0.18);
    color: #ff6ec7;
}
</style>
"""


def main() -> None:
    st.set_page_config(page_title="MusiMist", page_icon="🎵", layout="centered")
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    st.title("🎵 MusiMist")
    st.caption("RAG-grounded song recommendations with AI-generated explanations.")

    if not os.environ.get("ANTHROPIC_API_KEY"):
        st.info("No ANTHROPIC_API_KEY set — explanations will use the deterministic fallback.", icon="ℹ️")

    preset_name = st.selectbox("Start from a preset profile", list(PRESET_PROFILES.keys()))
    preset = PRESET_PROFILES[preset_name] or {}

    genres, moods = get_genres_and_moods()
    PLACEHOLDER = "— Select —"
    genre_options = [PLACEHOLDER] + genres
    mood_options = [PLACEHOLDER] + moods

    genre_index = genre_options.index(preset["genre"]) if preset.get("genre") in genre_options else 0
    mood_index = mood_options.index(preset["mood"]) if preset.get("mood") in mood_options else 0

    with st.form("preferences"):
        st.markdown("##### Tell us what you're in the mood for")
        col1, col2 = st.columns(2)
        with col1:
            genre = st.selectbox("Favorite genre", genre_options, index=genre_index)
            mood = st.selectbox("Current mood", mood_options, index=mood_index)
            tempo = st.number_input("Preferred tempo (BPM)", 0, 300, int(preset.get("tempo", 120)))
        with col2:
            energy = st.slider("Energy", 0.0, 1.0, float(preset.get("energy", 0.5)))
            valence = st.slider("Valence (positivity)", 0.0, 1.0, float(preset.get("valence", 0.5)))
            danceability = st.slider("Danceability", 0.0, 1.0, float(preset.get("danceability", 0.5)))
            acousticness = st.slider("Acousticness", 0.0, 1.0, float(preset.get("acousticness", 0.5)))

        k = st.slider("Number of recommendations", 1, 10, 5)
        submitted = st.form_submit_button("✨ Get recommendations")

    if not submitted:
        return

    if genre == PLACEHOLDER or mood == PLACEHOLDER:
        st.error(
            "Please select both a favorite genre and a current mood — "
            "we won't generate recommendations without them.",
            icon="⚠️",
        )
        return

    user_prefs = {
        "genre": genre, "mood": mood, "energy": energy, "valence": valence,
        "danceability": danceability, "acousticness": acousticness, "tempo": tempo,
    }
    user_prefs = {k_: v for k_, v in user_prefs.items() if v not in ("", None)}

    songs = get_songs()
    kb = get_knowledge_base()
    recommendations = recommend_songs(user_prefs, songs, k=k)

    with st.expander("Your profile", expanded=False):
        st.json(user_prefs)

    st.markdown("### Top recommendations")
    for rank, (song, score, reasons) in enumerate(recommendations, start=1):
        with st.container(border=True):
            st.markdown(
                f'<span class="song-rank-badge">{rank}</span>'
                f'<span class="song-title">{song["title"]}</span> '
                f'<span class="song-artist">— {song["artist"]}</span>',
                unsafe_allow_html=True,
            )
            st.progress(min(max(score, 0.0), 1.0), text=f"Score: {score:.2f}")
            st.caption(f"Reasons: {reasons or 'no strong matches'}")

            with st.spinner("Generating explanation..."):
                result = generate_explanation(kb, user_prefs, song, score, reasons)

            if result.used_llm:
                tag_html = '<span class="tag-pill tag-llm">🤖 LLM</span>'
                if not result.grounded:
                    tag_html += ' <span class="tag-pill tag-ungrounded">UNGROUNDED → FALLBACK</span>'
            else:
                tag_html = '<span class="tag-pill tag-fallback">📋 FALLBACK</span>'

            st.markdown(
                f'<div class="explanation-box">{tag_html}<br>{result.text}</div>',
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
