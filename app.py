import streamlit as st
import pandas as pd
import requests
import pickle
import html
import textwrap

# Helper function to remove all leading/trailing whitespace from HTML lines
# to prevent Streamlit's Markdown parser from rendering them as preformatted code.
def clean_html(html_str):
    return "\n".join([line.strip() for line in html_str.split("\n") if line.strip()])

# Set page config for a premium, wider layout
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inject custom CSS for stunning dark mode aesthetics and glassmorphism cards
st.markdown("""
<style>
    /* Main App Background and Typography */
    .stApp {
        background: radial-gradient(circle at top, #1e1b4b 0%, #0f0728 50%, #02000a 100%);
        color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header styling */
    .app-header {
        text-align: center;
        padding: 2rem 0;
        margin-bottom: 2rem;
        background: linear-gradient(180deg, rgba(30, 27, 75, 0.4) 0%, rgba(15, 7, 40, 0) 100%);
        border-bottom: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    .app-title {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.05em;
        background: linear-gradient(135deg, #a78bfa 0%, #ec4899 50%, #f43f5e 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .app-subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        font-weight: 400;
    }
    
    /* Control Box styling */
    .control-container {
        background: rgba(15, 23, 42, 0.4);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 2.5rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    
    /* Movie Cards styling */
    .movie-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 12px;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        margin-bottom: 1.5rem;
    }
    
    .movie-card:hover {
        transform: translateY(-8px);
        background: rgba(255, 255, 255, 0.07);
        border-color: rgba(167, 139, 250, 0.4);
        box-shadow: 0 12px 30px rgba(167, 139, 250, 0.15);
    }
    
    .poster-container {
        position: relative;
        overflow: hidden;
        border-radius: 10px;
        width: 100%;
        aspect-ratio: 2/3;
        margin-bottom: 12px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
    }
    
    .movie-poster {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.5s ease;
    }
    
    .movie-card:hover .movie-poster {
        transform: scale(1.05);
    }
    
    /* Synopsis Overlay */
    .poster-overlay {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(8, 5, 24, 0.92);
        color: #e2e8f0;
        opacity: 0;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        padding: 14px;
        box-sizing: border-box;
        font-size: 11px;
        line-height: 1.4;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: flex-start;
        text-align: left;
    }
    
    .poster-container:hover .poster-overlay {
        opacity: 1;
    }
    
    .overlay-title {
        font-weight: 700;
        font-size: 13px;
        color: #a78bfa;
        margin-bottom: 6px;
        border-bottom: 1px solid rgba(167, 139, 250, 0.2);
        padding-bottom: 4px;
        width: 100%;
    }
    
    .overlay-text {
        font-weight: 400;
        color: #cbd5e1;
    }
    
    .movie-title {
        color: #f8fafc;
        font-weight: 600;
        font-size: 14px;
        line-height: 1.3;
        margin: 6px 0 2px 0;
        /* Line clamping for titles that are too long */
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        overflow: hidden;
        text-overflow: ellipsis;
        height: 36px;
    }
    
    /* Fallback Poster Card styling */
    .fallback-poster {
        width: 100%;
        height: 100%;
        background: linear-gradient(135deg, #1e1b4b 0%, #311042 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        color: #a78bfa;
        font-size: 32px;
    }
    
    .fallback-icon {
        margin-bottom: 8px;
        filter: drop-shadow(0 0 8px rgba(167, 139, 250, 0.4));
    }
    
    .fallback-text {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #94a3b8;
    }
    
    /* Watch Providers styling */
    .providers-section {
        margin-top: 10px;
        border-top: 1px solid rgba(255, 255, 255, 0.05);
        padding-top: 8px;
        text-align: left;
        min-height: 48px;
        display: flex;
        flex-direction: column;
        justify-content: flex-end;
    }
    .providers-title {
        font-size: 9px;
        text-transform: uppercase;
        color: #94a3b8;
        font-weight: 700;
        margin-bottom: 5px;
        letter-spacing: 0.05em;
    }
    .providers-list {
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
        align-items: center;
    }
    .provider-logo {
        width: 22px;
        height: 22px;
        border-radius: 4px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.3);
        transition: transform 0.2s;
    }
    .provider-logo:hover {
        transform: scale(1.15);
    }
    .no-providers {
        font-size: 10px;
        color: #64748b;
        font-style: italic;
    }
    
    /* Selected Movie Featured Card */
    .featured-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 2rem;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
        display: flex;
        gap: 24px;
        align-items: center;
        text-align: left;
    }
    @media (max-width: 768px) {
        .featured-card {
            flex-direction: column;
            text-align: center;
        }
    }
    .featured-poster {
        width: 130px;
        border-radius: 10px;
        box-shadow: 0 8px 20px rgba(0,0,0,0.5);
        object-fit: cover;
    }
    .featured-info {
        flex: 1;
    }
    .featured-badge {
        background: linear-gradient(135deg, #7c3aed 0%, #db2777 100%);
        color: white;
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 9px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        display: inline-block;
        margin-bottom: 8px;
    }
    .featured-title {
        font-size: 24px;
        font-weight: 800;
        color: white;
        margin: 0 0 10px 0;
    }
    .featured-overview {
        font-size: 13.5px;
        color: #cbd5e1;
        line-height: 1.5;
        margin: 0;
    }
    
    /* Streamlit widgets overrides to match styling */
    div[data-baseweb="select"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border-radius: 8px !important;
    }
    
    button[kind="secondaryFormSubmit"], button[kind="secondary"] {
        background: linear-gradient(135deg, #7c3aed 0%, #db2777 100%) !important;
        color: white !important;
        border: none !important;
        font-weight: 600 !important;
        padding: 0.5rem 2rem !important;
        border-radius: 8px !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 12px rgba(124, 58, 237, 0.25) !important;
    }
    
    button[kind="secondaryFormSubmit"]:hover, button[kind="secondary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.4) !important;
    }
</style>
""", unsafe_allow_html=True)

# Define clean top header banner
st.markdown("""
<div class="app-header">
    <div class="app-title">MOVIE RECOMMENDATION SYSTEM</div>
    <div class="app-subtitle">Discover your next cinematic masterpiece with AI recommendation engine</div>
</div>
""", unsafe_allow_html=True)

# Load data with caching
@st.cache_resource
def load_data():
    with open('movie_data.pkl', 'rb') as file:
        return pickle.load(file)

movies, cosine_sim = load_data()

# Function to get movie recommendations
def get_recommendations(title, cosine_sim=cosine_sim):
    try:
        idx = movies[movies['title'] == title].index[0]
        sim_scores = list(enumerate(cosine_sim[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        sim_scores = sim_scores[1:11]  # Get top 10 similar movies
        movie_indices = [i[0] for i in sim_scores]
        return movies[['title', 'movie_id', 'overview']].iloc[movie_indices]
    except Exception as e:
        st.error(f"Error fetching recommendations: {str(e)}")
        return pd.DataFrame(columns=['title', 'movie_id', 'overview'])

# Fetch movie poster from TMDB API with caching
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id):
    try:
        api_key = '7b995d3c6fd91a2284b4ad8cb390c7b8'
        # Fixed: Switch the blocked endpoint api.themoviedb.org to api.tmdb.org
        url = f'https://api.tmdb.org/3/movie/{movie_id}?api_key={api_key}'
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if 'poster_path' in data and data['poster_path']:
                poster_path = data['poster_path']
                return f"https://image.tmdb.org/t/p/w500{poster_path}"
        return None
    except Exception:
        # Silently fail network calls to prevent breaking UI with st.warning boxes
        return None

# Fetch watch providers from TMDB API with caching
@st.cache_data(show_spinner=False)
def fetch_watch_providers(movie_id):
    try:
        api_key = '7b995d3c6fd91a2284b4ad8cb390c7b8'
        url = f'https://api.tmdb.org/3/movie/{movie_id}/watch/providers?api_key={api_key}'
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            results = response.json().get('results', {})
            # Try India (IN) first, then fallback to United States (US), then fallback to any available region
            prov_data = results.get('IN', {})
            if not prov_data or not (prov_data.get('flatrate') or prov_data.get('rent') or prov_data.get('buy')):
                prov_data = results.get('US', {})
            if not prov_data or not (prov_data.get('flatrate') or prov_data.get('rent') or prov_data.get('buy')):
                for reg, data in results.items():
                    if data.get('flatrate') or data.get('rent') or data.get('buy'):
                        prov_data = data
                        break
            
            providers = []
            if 'flatrate' in prov_data:
                for p in prov_data['flatrate']:
                    providers.append({
                        'name': p['provider_name'],
                        'logo': f"https://image.tmdb.org/t/p/original{p['logo_path']}" if p.get('logo_path') else None,
                        'type': 'Stream'
                    })
            elif 'rent' in prov_data:
                for p in prov_data['rent'][:3]:  # Top 3
                    providers.append({
                        'name': p['provider_name'],
                        'logo': f"https://image.tmdb.org/t/p/original{p['logo_path']}" if p.get('logo_path') else None,
                        'type': 'Rent'
                    })
            elif 'buy' in prov_data:
                for p in prov_data['buy'][:3]:  # Top 3
                    providers.append({
                        'name': p['provider_name'],
                        'logo': f"https://image.tmdb.org/t/p/original{p['logo_path']}" if p.get('logo_path') else None,
                        'type': 'Buy'
                    })
            return providers
        return []
    except Exception:
        return []

# Initialize session state for recommendations
if 'recommendations' not in st.session_state:
    st.session_state.recommendations = None
if 'last_selected' not in st.session_state:
    st.session_state.last_selected = None

# Wrap search section in a custom visual block
st.markdown('<div class="control-container">', unsafe_allow_html=True)
selected_movie = st.selectbox("Search and select a movie:", movies['title'].values)
recommend_button = st.button('Get Recommendations')
st.markdown('</div>', unsafe_allow_html=True)

if recommend_button:
    with st.spinner("Analyzing similarity vectors and fetching movie details..."):
        recs = get_recommendations(selected_movie)
        if not recs.empty:
            st.session_state.recommendations = recs
            st.session_state.last_selected = selected_movie
        else:
            st.warning("No recommendations could be generated for this movie.")

# Render recommendations if they exist in state
if st.session_state.recommendations is not None and st.session_state.last_selected is not None:
    current_movie = st.session_state.last_selected
    recommendations = st.session_state.recommendations
    
    # Get details of the selected movie
    selected_movie_row = movies[movies['title'] == current_movie].iloc[0]
    selected_id = selected_movie_row['movie_id']
    # Safely get overview
    raw_selected_overview = selected_movie_row['overview']
    selected_overview = raw_selected_overview if isinstance(raw_selected_overview, str) and raw_selected_overview else "No synopsis available."
    
    escaped_selected_title = html.escape(current_movie)
    escaped_selected_overview = html.escape(selected_overview)
    
    selected_poster = fetch_poster(selected_id)
    selected_providers = fetch_watch_providers(selected_id)
    
    # Watch providers HTML for the featured card
    featured_providers_html = ""
    if selected_providers:
        featured_providers_list = "".join([
            f'<img src="{p["logo"]}" class="provider-logo" title="{html.escape(p["name"])} ({p["type"]})" style="width: 24px; height: 24px;" alt="{html.escape(p["name"])}" />'
            for p in selected_providers if p.get("logo")
        ])
        featured_providers_html = textwrap.dedent(f'''
        <div style="margin-top: 15px; display: flex; align-items: center; gap: 10px;">
            <span style="font-size: 10px; text-transform: uppercase; color: #94a3b8; font-weight: 700; letter-spacing: 0.05em;">Available on:</span>
            <div class="providers-list">{featured_providers_list}</div>
        </div>
        ''')
    
    # Featured selected movie poster image
    if selected_poster:
        poster_img_html = f'<img src="{selected_poster}" class="featured-poster" alt="{escaped_selected_title}" />'
    else:
        poster_img_html = textwrap.dedent('''
        <div class="fallback-poster" style="width: 130px; height: 195px; border-radius: 10px;">
            <div class="fallback-icon">🎬</div>
            <div class="fallback-text">No Poster</div>
        </div>
        ''')
        
    # Featured card HTML banner
    featured_card_html = textwrap.dedent(f'''
    <div class="featured-card">
        {poster_img_html}
        <div class="featured-info">
            <span class="featured-badge">Currently Selected</span>
            <h2 class="featured-title">{escaped_selected_title}</h2>
            <p class="featured-overview">{escaped_selected_overview}</p>
            {featured_providers_html}
        </div>
    </div>
    ''')
    st.markdown(clean_html(featured_card_html), unsafe_allow_html=True)
    
    st.markdown('<h3 style="margin-top: 2rem; margin-bottom: 1.5rem; color: #a78bfa;">More Movies Like This:</h3>', unsafe_allow_html=True)
    
    # Create a 2x5 grid layout
    for i in range(0, 10, 5):  # Loop over rows (2 rows, 5 movies each)
        cols = st.columns(5)  # Create 5 columns for each row
        for col, j in zip(cols, range(i, i+5)):
            if j < len(recommendations):
                movie_title = recommendations.iloc[j]['title']
                movie_id = recommendations.iloc[j]['movie_id']
                # Safely grab overview, handling missing or empty descriptions
                raw_overview = recommendations.iloc[j]['overview']
                overview = raw_overview if isinstance(raw_overview, str) and raw_overview else "No synopsis available."
                
                # HTML escaping for security and formatting safety
                escaped_movie_title = html.escape(movie_title)
                escaped_overview = html.escape(overview)
                
                poster_url = fetch_poster(movie_id)
                providers = fetch_watch_providers(movie_id)
                
                # Generate HTML for watch providers
                providers_html = ""
                if providers:
                    providers_list_html = "".join([
                        f'<div class="provider-icon-wrapper">'
                        f'<img src="{p["logo"]}" class="provider-logo" title="{html.escape(p["name"])} ({p["type"]})" alt="{html.escape(p["name"])}" />'
                        f'</div>'
                        for p in providers if p.get("logo")
                    ])
                    providers_html = textwrap.dedent(f'''
                    <div class="providers-section">
                        <div class="providers-title">Watch on:</div>
                        <div class="providers-list">
                            {providers_list_html}
                        </div>
                    </div>
                    ''')
                else:
                    providers_html = textwrap.dedent(f'''
                    <div class="providers-section">
                        <div class="providers-title">Watch on:</div>
                        <div class="no-providers">No Stream Info</div>
                    </div>
                    ''')
                
                with col:
                    if poster_url:
                        poster_html = f'<img src="{poster_url}" class="movie-poster" alt="{escaped_movie_title}" />'
                    else:
                        poster_html = textwrap.dedent('''
                        <div class="fallback-poster">
                            <div class="fallback-icon">🎬</div>
                            <div class="fallback-text">No Poster</div>
                        </div>
                        ''')
                        
                    card_html = textwrap.dedent(f'''
                    <div class="movie-card">
                        <div class="poster-container">
                            {poster_html}
                            <div class="poster-overlay">
                                <div class="overlay-title">{escaped_movie_title}</div>
                                <div class="overlay-text">{escaped_overview}</div>
                            </div>
                        </div>
                        <div class="movie-title" title="{escaped_movie_title}">{escaped_movie_title}</div>
                        {providers_html}
                    </div>
                    ''')
                    st.markdown(clean_html(card_html), unsafe_allow_html=True)
