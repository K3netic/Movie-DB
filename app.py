import streamlit as st
import urllib.parse
from google import genai

# Set page layout to wide and mobile-friendly
st.set_page_config(page_title="Personal Movie DB", page_icon="🎬", layout="wide")

# Initialize Gemini Client using Streamlit Secrets
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    ai_available = True
except Exception:
    ai_available = False

py_url_format = lambda title, site: f"https://www.{'azmen' if site == 'men' else 'aznude'}.com/search.html?q={urllib.parse.quote(title)}"

# Sample local database
MOVIE_DATABASE = [
    {
        "id": "1",
        "title": "Shortbus",
        "year": 2006,
        "genre": ["Comedy", "Drama"],
        "rating": 6.4,
        "synopsis": "A group of interconnected New Yorkers navigate intimacy, art, and relationships through an underground artistic salon.",
        "tags": ["lgbt", "unsimulated sex", "indie", "new york", "ensemble"]
    },
    {
        "id": "2",
        "title": "Forgetting Sarah Marshall",
        "year": 2008,
        "genre": ["Comedy", "Romance"],
        "rating": 7.1,
        "synopsis": "Devastated by a sudden breakup, a struggling musician takes a Hawaiian vacation, only to find his ex-girlfriend staying at the same resort with her new rockstar boyfriend.",
        "tags": ["comedy", "full frontal", "male nudity", "breakup", "hawaii"]
    },
    {
        "id": "3",
        "title": "Rotting in the Sun",
        "year": 2023,
        "genre": ["Comedy", "Mystery"],
        "rating": 6.4,
        "synopsis": "A dark, satirical comedy exploring Mexico City's queer social scenes when a filmmaker suddenly disappears.",
        "tags": ["lgbt", "dark comedy", "satire", "unsimulated sex", "mexico city"]
    }
]

# App Title & Header
st.title("🎬 Personal Movie Search")
st.caption("AI-Powered Mobile Database")

# Sidebar Filters
st.sidebar.header("🔍 Traditional Filters")
all_genres = list(set(g for movie in MOVIE_DATABASE for g in movie["genre"]))
selected_genres = st.sidebar.multiselect("Filter by Genre", options=all_genres)
min_rating = st.sidebar.slider("Minimum Rating", min_value=1.0, max_value=10.0, value=6.0, step=0.1)

# AI Smart Search Section
st.subheader("🤖 AI Conversational Search")
ai_query = st.text_input("Ask the AI anything about your database:", placeholder="e.g. Find me a dark comedy from recent years...")

# AI filtering logic or fallback to keyword filtering
filtered_movies = []
ai_recommendation_text = ""

if ai_query.strip() and ai_available:
    with st.spinner("AI is searching your database..."):
        db_summary = "\n".join([f"ID: {m['id']}, Title: {m['title']} ({m['year']}), Genre: {m['genre']}, Synopsis: {m['synopsis']}, Tags: {m['tags']}" for m in MOVIE_DATABASE])
        
        prompt = f"""
        You are a smart movie database assistant. Here is the user's movie database:
        {db_summary}
        
        The user is searching for: "{ai_query}"
        
        1. Select which movie IDs from the database match this request.
        2. Provide a short, friendly 1-sentence explanation of why it matches.
        Format your response strictly as a comma-separated list of matching IDs, followed by a pipe character (|), followed by your explanation. Example: 1,3 | These films match your request for dark/indie themes.
        If none match, reply with "NONE | No matching films found."
        """
        
        try:
            # Updated to current model identifier
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt
            )
            
            parts = response.text.strip().split("|")
            matching_ids = [i.strip() for i in parts[0].split(",") if i.strip().isdigit()]
            ai_recommendation_text = parts[1].strip() if len(parts) > 1 else ""
            
            for movie in MOVIE_DATABASE:
                if movie["id"] in matching_ids and movie["rating"] >= min_rating:
                    filtered_movies.append(movie)
        except Exception as e:
            ai_recommendation_text = f"AI error occurred: {str(e)}"
            
# If no AI query was typed, use standard filtering
if not ai_query.strip():
    for movie in MOVIE_DATABASE:
        if movie["rating"] < min_rating:
            continue
        if selected_genres and not any(g in movie["genre"] for g in selected_genres):
            continue
        filtered_movies.append(movie)

# Display AI Insights if active
if ai_query.strip() and ai_available and ai_recommendation_text:
    st.info(f"💡 **AI Insight:** {ai_recommendation_text}")

# Results Display
st.markdown("---")
st.subheader(f"Results ({len(filtered_movies)})")

if not filtered_movies:
    st.info("No movies found matching your query or filters.")
else:
    for movie in filtered_movies:
        with st.container():
            st.markdown(f"### {movie['title']} ({movie['year']})")
            st.write(f"**Rating:** ⭐ {movie['rating']}/10 | **Genres:** {', '.join(movie['genre'])}")
            st.write(f"**Synopsis:** {movie['synopsis']}")
            
            tags_formatted = " ".join([f"`#{tag}`" for tag in movie['tags']])
            st.markdown(f"**Tags:** {tags_formatted}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.link_button("🌐 Search on AZNude", py_url_format(movie["title"], "aznude"))
            with col2:
                st.link_button("🌐 Search on AZMen", py_url_format(movie["title"], "men"))
            
            st.divider()
