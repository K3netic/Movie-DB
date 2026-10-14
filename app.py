import streamlit as st
import urllib.parse
from google import genai

# Set page layout to wide and mobile-friendly
st.set_page_config(page_title="Personal Film Nudity & Search DB", page_icon="🎬", layout="wide")

# Initialize Gemini Client
try:
    client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    ai_available = True
except Exception:
    ai_available = False

py_url_format = lambda title, site: f"https://www.{'azmen' if site == 'men' else 'aznude'}.com/search.html?q={urllib.parse.quote(title)}"

# Initialize Session State Database with expanded IMDb metadata and 'watched' tracking
if "movie_database" not in st.session_state:
    st.session_state.movie_database = [
        {
            "id": "1",
            "title": "Shortbus",
            "year": 2006,
            "release_date": "2006-10-06",
            "language": "English",
            "genre": ["Comedy", "Drama"],
            "rating": 6.4,
            "synopsis": "A group of interconnected New Yorkers navigate intimacy, art, and relationships through an underground artistic salon.",
            "nudity_tags": ["Male Nudity", "Female Nudity", "Unsimulated Sex"],
            "watched": False
        },
        {
            "id": "2",
            "title": "Forgetting Sarah Marshall",
            "year": 2008,
            "release_date": "2008-04-18",
            "language": "English",
            "genre": ["Comedy", "Romance"],
            "rating": 7.1,
            "synopsis": "Devastated by a sudden breakup, a struggling musician takes a Hawaiian vacation, only to find his ex-girlfriend staying at the same resort with her new rockstar boyfriend.",
            "nudity_tags": ["Male Nudity", "Female Nudity", "Full Frontal"],
            "watched": True
        },
        {
            "id": "3",
            "title": "Rotting in the Sun",
            "year": 2023,
            "release_date": "2023-09-08",
            "language": "English / Spanish",
            "genre": ["Comedy", "Mystery"],
            "rating": 6.4,
            "synopsis": "A dark, satirical comedy exploring Mexico City's queer social scenes when a filmmaker suddenly disappears.",
            "nudity_tags": ["Male Nudity", "Unsimulated Sex"],
            "watched": False
        }
    ]

# App Title & Header
st.title("🎬 Film Nudity & Search Database")
st.caption("Custom Mobile Index with IMDb Metadata & AZNude Links")

# --- SIDEBAR FILTERS ---
st.sidebar.header("🔍 Filters & Controls")

# Watched Status Filter
watched_filter = st.sidebar.selectbox("Show Status:", ["All Films", "Unwatched Only", "Watched Only"])

# Nudity Filter
all_nudity_options = sorted(list(set(tag for m in st.session_state.movie_database for tag in m["nudity_tags"])))
selected_nudity = st.sidebar.multiselect("Filter by Nudity Content:", options=all_nudity_options)

# Minimum Rating Slider
min_rating = st.sidebar.slider("Minimum Rating", min_value=1.0, max_value=10.0, value=6.0, step=0.1)

st.sidebar.markdown("---")
st.sidebar.subheader("➕ Add Custom Film Entry")
with st.sidebar.form("add_movie_form"):
    new_title = st.text_input("Title")
    new_year = st.number_input("Year", min_value=1900, max_value=2030, value=2024)
    new_lang = st.text_input("Language", value="English")
    new_rating = st.slider("Rating", 1.0, 10.0, 6.5, 0.1)
    new_synopsis = st.text_area("Synopsis")
    new_nudity = st.multiselect("Nudity Tags", ["Male Nudity", "Female Nudity", "Full Frontal", "Unsimulated Sex"])
    
    submitted = st.form_submit_button("Add to Database")
    if submitted and new_title:
        new_id = str(len(st.session_state.movie_database) + 1)
        st.session_state.movie_database.append({
            "id": new_id,
            "title": new_title,
            "year": int(new_year),
            "release_date": f"{int(new_year)}-01-01",
            "language": new_lang,
            "genre": ["Drama"],
            "rating": float(new_rating),
            "synopsis": new_synopsis,
            "nudity_tags": new_nudity,
            "watched": False
        })
        st.sidebar.success(f"Added {new_title}!")
        st.rerun()

# --- MAIN SEARCH AREA ---
st.subheader("🔎 Search Database")
search_query = st.text_input("Search by title, language, or keyword:", placeholder="e.g. English, New York, Comedy...")

# Filtering Logic
filtered_movies = []

for movie in st.session_state.movie_database:
    # 1. Rating check
    if movie["rating"] < min_rating:
        continue
        
    # 2. Watched filter check
    if watched_filter == "Unwatched Only" and movie["watched"]:
        continue
    if watched_filter == "Watched Only" and not movie["watched"]:
        continue
        
    # 3. Nudity filter check (must match all selected nudity tags if any are chosen)
    if selected_nudity:
        if not all(tag in movie["nudity_tags"] for tag in selected_nudity):
            continue
            
    # 4. Text / Keyword search check
    if search_query.strip():
        q = search_query.lower().strip()
        in_title = q in movie["title"].lower()
        in_synopsis = q in movie["synopsis"].lower()
        in_lang = q in movie["language"].lower()
        if not (in_title or in_synopsis or in_lang):
            continue
            
    filtered_movies.append(movie)

# Results Display
st.markdown("---")
st.subheader(f"Results ({len(filtered_movies)})")

if not filtered_movies:
    st.info("No films found matching your active filters.")
else:
    for i, movie in enumerate(filtered_movies):
        with st.container():
            # Header info with watched status indicator
            status_icon = "✅ Watched" if movie["watched"] else "📌 Unwatched"
            st.markdown(f"### {movie['title']} ({movie['year']}) — *{status_icon}*")
            
            st.write(f"**Rating:** ⭐ {movie['rating']}/10 | **Language:** {movie['language']} | **Released:** {movie['release_date']}")
            st.write(f"**Synopsis:** {movie['synopsis']}")
            
            # Nudity Content Tags
            nudity_formatted = " ".join([f"`{tag}`" for tag in movie['nudity_tags']])
            st.markdown(f"**Content Flags:** {nudity_formatted if nudity_formatted else 'None specified'}")
            
            # Action Buttons: AZNude/AZMen + Mark as Watched Toggle
            col1, col2, col3 = st.columns(3)
            with col1:
                st.link_button("🌐 AZNude Search", py_url_format(movie["title"], "aznude"))
            with col2:
                st.link_button("🌐 AZMen Search", py_url_format(movie["title"], "men"))
            with col3:
                # Find original index in session state to toggle watched state accurately
                original_index = next(idx for idx, m in enumerate(st.session_state.movie_database) if m["id"] == movie["id"])
                btn_label = "Mark Unwatched" if movie["watched"] else "Mark Watched"
                if st.button(btn_label, key=f"watch_btn_{movie['id']}"):
                    st.session_state.movie_database[original_index]["watched"] = not movie["watched"]
                    st.rerun()
            
            st.divider()
