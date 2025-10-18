import streamlit as st
import pickle
import requests
import os

# Load movies dataset
movies = pickle.load(open("movies.pkl", "rb"))

# Google Drive file ID
file_id = "1XsTpNx726M2LmJAeEOr3aBIMh6UD8atR"
similarity_file = "similarity.pkl"

# Function to download large Google Drive files safely
def download_file_from_google_drive(id, destination):
    URL = "https://docs.google.com/uc?export=download"

    session = requests.Session()
    response = session.get(URL, params={'id': id}, stream=True)
    token = None

    # Check for large file confirmation token
    for key, value in response.cookies.items():
        if key.startswith('download_warning'):
            token = value

    if token:
        params = {'id': id, 'confirm': token}
        response = session.get(URL, params=params, stream=True)

    CHUNK_SIZE = 32768
    with open(destination, "wb") as f:
        for chunk in response.iter_content(CHUNK_SIZE):
            if chunk:
                f.write(chunk)

# Download similarity.pkl if it doesn't exist
if not os.path.exists(similarity_file):
    with st.spinner("Downloading similarity file..."):
        download_file_from_google_drive(file_id, similarity_file)

# Load similarity matrix safely
with open(similarity_file, "rb") as f:
    similarity = pickle.load(f)

# ========== Movie Recommendation Functions ==========
def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return None

def recommend(movie):
    movie_index = movies[movies['title'] == movie].index[0]
    distances = similarity[movie_index]
    movies_l = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

    recommended_movies = []
    recommended_movies_posters = []

    for i in movies_l:
        movie_id = movies.iloc[i[0]].id
        recommended_movies.append(movies.iloc[i[0]].title)
        recommended_movies_posters.append(fetch_poster(movie_id))

    return recommended_movies, recommended_movies_posters

# ========== Streamlit UI ==========
st.title('🎬 Movie Recommendation System')

selected_movie_name = st.selectbox("Choose a movie", options=movies['title'].values)

if st.button('Show Recommendation'):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        col.text(names[idx])
        if posters[idx]:
            col.image(posters[idx])
