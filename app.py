import streamlit as st

# Set page layout to wide and mobile-friendly
st.set_page_config(page_title="Personal Movie DB", page_icon="🎬", layout="wide")

# Sample local database containing movies, metadata, tags, and custom external links
MOVIE_DATABASE = [
    {
        "id": "1",
        "title": "Shortbus",
        "year": 2006,
        "genre": ["Comedy", "Drama"],
        "rating": 6.4,
        "synopsis": "A group of interconnected New Yorkers navigate intimacy, art, and relationships through an underground artistic salon.",
        "tags": ["lgbt", "unsimulated sex", "indie", "new york", "ensemble"],
        "aznude_url": "https://www.aznude.com/aznude/search/shortbus",
        "men_aznude_url": "https://men.aznude.com/search/shortbus"
    },
    {
        "id": "2",
        "title": "Forgetting Sarah Marshall",
        "year": 2008,
        "genre": ["Comedy", "Romance"],
        "rating": 7.1,
        "synopsis": "Devastated by a sudden breakup, a struggling musician takes a Hawaiian vacation, only to find his ex-girlfriend staying at the same resort with her new rockstar boyfriend.",
        "tags": ["comedy", "full frontal", "male nudity", "breakup", "hawaii"],
        "aznude_url": "https://www.aznude.com/aznude/search/forgetting-sarah-marshall",
        "men_aznude_url": "https://men.aznude.com/search/forgetting-sarah-marshall"
    },
    {
        "id": "3",
        "title": "Rotting in the Sun",
        "year": 2023,
        "genre": ["Comedy", "Mystery"],
        "rating": 6.4,
        "synopsis": "A dark, satirical comedy exploring Mexico City's queer social scenes when a filmmaker suddenly disappears.",
        "tags": ["lgbt", "dark comedy", "satire", "unsimulated sex", "mexico city"],
        "aznude_url": "https://www.aznude.com/aznude/search/rotting-in-the-sun",
        "men_aznude_url": "https://men.aznude.com/search/rotting-in-the-sun"
    }
]

# App Title & Header
st.title("🎬 Personal Movie Search")
st.caption("Mobile-optimized personal database with external site indexing.")

# Sidebar Filters
st.sidebar.header("🔍 Traditional Filters")

# Genre Multi-select
all_genres = list(set(g for movie in MOVIE_DATABASE for g in movie["genre"]))
selected_genres = st.sidebar.multiselect("Filter by Genre", options=all_genres)

# Minimum Rating Slider
min_rating = st.sidebar.slider("Minimum Rating", min_value=1.0, max_value=10.0, value=6.0, step=0.1)

# Natural Language / Keyword Search Input
st.subheader("Smart Keyword Search")
search_query = st.text_input("Search by keyword, tag, actor, or title:", placeholder="e.g. lgbt, hawaii, dark comedy...")

# Filtering Logic
filtered_movies = []

for movie in MOVIE_DATABASE:
    # 1. Rating check
    if movie["rating"] < min_rating:
        continue
    
    # 2. Genre check
    if selected_genres and not any(g in movie["genre"] for g in selected_genres):
        continue
        
    # 3. Keyword / Text search check
    if search_query.strip():
        q = search_query.lower().strip()
        in_title = q in movie["title"].lower()
        in_synopsis = q in movie["synopsis"].lower()
        in_tags = any(q in tag for tag in movie["tags"])
        
        if not (in_title or in_synopsis or in_tags):
            continue
            
    filtered_movies.append(movie)

# Results Display
st.markdown("---")
st.subheader(f"Results ({len(filtered_movies)})")

if not filtered_movies:
    st.info("No movies found matching your current filters.")
else:
    for movie in filtered_movies:
        with st.container():
            st.markdown(f"### {movie['title']} ({movie['year']})")
            st.write(f"**Rating:** ⭐ {movie['rating']}/10 | **Genres:** {', '.join(movie['genre'])}")
            st.write(f"**Synopsis:** {movie['synopsis']}")
            
            # Tags Pills
            tags_formatted = " ".join([f"`#{tag}`" for tag in movie['tags']])
            st.markdown(f"**Tags:** {tags_formatted}")
            
            # Action / Integration Links
            col1, col2 = st.columns(2)
            with col1:
                st.link_button("🌐 View on AZNude", movie["aznude_url"])
            with col2:
                st.link_button("🌐 View on Men.AZNude", movie["men_aznude_url"])
            
            st.divider()
