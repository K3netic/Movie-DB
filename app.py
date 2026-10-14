import streamlit as st
import urllib.parse
import requests
import sqlite3
import os
from google import genai

# Set page layout to wide and mobile-friendly
st.set_page_config(page_title="Master Film & TV Nudity Index", page_icon="🎬", layout="wide")

# Initialize Gemini Client
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    ai_available = True
except Exception:
    ai_available = False

tmdb_api_key = st.secrets.get("TMDB_API_KEY", "")

# Helper for AZNude / AZMen search links
py_url_format = lambda title, site: f"https://www.{'azmen' if site == 'men' else 'aznude'}.com/search.html?q={urllib.parse.quote(title)}"

# --- SQLITE DATABASE SETUP FOR WATCHLIST & TAGS ---
DB_FILE = "user_watchlist.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS watchlist (
            media_id TEXT PRIMARY KEY,
            title TEXT,
            media_type TEXT,
            year TEXT,
            watched INTEGER,
            nudity_tags TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_watched_status(media_id):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT watched, nudity_tags FROM watchlist WHERE media_id = ?", (media_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return bool(row[0]), row[1].split(",") if row[1] else []
    return False, []

def toggle_watched_status(media_id, title, media_type, year, nudity_tags):
    current_status, existing_tags = get_watched_status(media_id)
    new_status = not current_status
    tags_str = ",".join(nudity_tags)
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO watchlist (media_id, title, media_type, year, watched, nudity_tags)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(media_id) DO UPDATE SET watched = ?
    ''', (media_id, title, media_type, year, int(new_status), tags_str, int(new_status)))
    conn.commit()
    conn.close()

def get_all_saved_items():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT media_id, title, media_type, year, watched, nudity_tags FROM watchlist")
    rows = c.fetchall()
    conn.close()
    return rows

init_db()

# --- APP UI ---
st.title("🎬 Master Film & TV Search")
st.caption("Live Search Across All Movies & TV Shows with Nudity Flags & AZNude Links")

# Navigation Tabs
tab_search, tab_watchlist = st.tabs(["🔎 Global Search", "📋 My Saved / Watched List"])

# ==========================================
# TAB 1: GLOBAL ON-DEMAND SEARCH
# ==========================================
with tab_search:
    st.subheader("Search Master Database")
    
    col_q, col_type = st.columns([3, 1])
    with col_q:
        search_query = st.text_input("Enter any movie or TV show title:", placeholder="e.g. Shortbus, Game of Thrones, Euphoria...")
    with col_type:
        media_type_choice = st.selectbox("Type:", ["All", "Movie", "TV Show"])

    # Content & Rating Filters
    st.markdown("#### Filters")
    f_col1, f_col2 = st.columns(2)
    with f_col1:
        min_rating = st.slider("Minimum Rating:", 1.0, 10.0, 6.0, 0.1)
    with f_col2:
        nudity_filter = st.multiselect("Nudity Content Flags:", ["Male Nudity", "Female Nudity", "Full Frontal", "Unsimulated Sex"])

    if search_query.strip():
        if not tmdb_api_key:
            st.error("Please add `TMDB_API_KEY` to Streamlit Secrets to enable live global search.")
        else:
            with st.spinner(f"Searching global database for '{search_query}'..."):
                try:
                    # Query TMDB Live Search API
                    search_url = f"https://api.themoviedb.org/3/search/multi?api_key={tmdb_api_key}&query={urllib.parse.quote(search_query)}"
                    res = requests.get(search_url).json()
                    results = res.get("results", [])
                    
                    filtered_results = []
                    for item in results:
                        m_type = item.get("media_type")
                        if media_type_choice == "Movie" and m_type != "movie":
                            continue
                        if media_type_choice == "TV Show" and m_type != "tv":
                            continue
                        if m_type not in ["movie", "tv"]:
                            continue
                            
                        rating = round(item.get("vote_average", 0.0), 1)
                        if rating < min_rating:
                            continue
                            
                        filtered_results.append(item)
                    
                    st.success(f"Found {len(filtered_results)} matching titles")
                    st.divider()

                    for item in filtered_results:
                        m_id = str(item.get("id"))
                        m_type = item.get("media_type")
                        title = item.get("title") if m_type == "movie" else item.get("name")
                        release_date = item.get("release_date") if m_type == "movie" else item.get("first_air_date")
                        year = release_date[:4] if release_date else "N/A"
                        rating = round(item.get("vote_average", 0.0), 1)
                        synopsis = item.get("overview", "No synopsis available.")
                        lang = item.get("original_language", "en").upper()
                        
                        # Get saved status from local SQLite DB
                        is_watched, saved_tags = get_watched_status(m_id)
                        
                        # Check nudity filter if selected
                        if nudity_filter and not any(f in saved_tags for f in nudity_filter):
                            # Default tags based on synopsis if not manually tagged yet
                            synopsis_lower = synopsis.lower()
                            has_flag = False
                            if "male nudity" in nudity_filter and ("male nudity" in synopsis_lower or "unsimulated" in synopsis_lower):
                                has_flag = True
                            if "female nudity" in nudity_filter and ("female nudity" in synopsis_lower or "topless" in synopsis_lower):
                                has_flag = True
                            if "unsimulated sex" in nudity_filter and "unsimulated" in synopsis_lower:
                                has_flag = True
                            if not has_flag and nudity_filter:
                                continue

                        # Card Rendering
                        with st.container():
                            status_badge = "✅ Watched" if is_watched else "📌 Unwatched"
                            type_badge = "🎬 Movie" if m_type == "movie" else "📺 TV Series"
                            
                            st.markdown(f"### {title} ({year}) — *{type_badge}* [{status_badge}]")
                            st.write(f"**Rating:** ⭐ {rating}/10 | **Language:** {lang} | **Released:** {release_date}")
                            st.write(f"**Synopsis:** {synopsis}")
                            
                            # Action Buttons
                            b_col1, b_col2, b_col3 = st.columns(3)
                            with b_col1:
                                st.link_button("🌐 AZNude Search", py_url_format(title, "aznude"))
                            with b_col2:
                                st.link_button("🌐 AZMen Search", py_url_format(title, "men"))
                            with b_col3:
                                watch_label = "Mark Unwatched" if is_watched else "Mark Watched"
                                if st.button(watch_label, key=f"global_w_{m_id}"):
                                    toggle_watched_status(m_id, title, m_type, year, saved_tags)
                                    st.rerun()
                            
                            st.divider()

                except Exception as e:
                    st.error(f"Error executing search: {str(e)}")

# ==========================================
# TAB 2: MY SAVED WATCHLIST & TRACKER
# ==========================================
with tab_watchlist:
    st.subheader("Your Personal Watchlist & History")
    saved_items = get_all_saved_items()
    
    if not saved_items:
        st.info("You haven't marked any films or TV shows yet. Search titles in the Global Search tab and tap 'Mark Watched' to track them here!")
    else:
        for m_id, title, m_type, year, watched, tags_str in saved_items:
            status_text = "✅ Watched" if watched else "📌 Saved / Unwatched"
            type_text = "🎬 Movie" if m_type == "movie" else "📺 TV Series"
            
            with st.container():
                st.markdown(f"### {title} ({year}) — {type_text}")
                st.write(f"**Status:** {status_text}")
                
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.link_button("🌐 AZNude Search", py_url_format(title, "aznude"))
                with c2:
                    st.link_button("🌐 AZMen Search", py_url_format(title, "men"))
                with c3:
                    if st.button("Toggle Watched Status", key=f"tab2_w_{m_id}"):
                        toggle_watched_status(m_id, title, m_type, year, tags_str.split(",") if tags_str else [])
                        st.rerun()
                st.divider()
