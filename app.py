import streamlit as st
import pickle
import requests
import os

# Load movies dataset
movies = pickle.load(open("movies.pkl", "rb"))

# Google Drive file ID
file_id = "1XsTpNx726M2LmJAeEOr3aBIMh6UD8atR"
similarity_file = "similarity.pkl"

# Download similarity.pkl only if it doesn't exist
if not os.path.exists(similarity_file):
    url = f"https://drive.google.com/uc?export=download&id={file_id}"
    response = requests.get(url)
    with open(similarity_file, "wb") as f:
        f.write(response.content)

# Load similarity matrix
with open(similarity_file, "rb") as f:
    similarity = pickle.load(f)


def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US"
    data = requests.get(url).json()
    poster_path = data.get('poster_path')
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    else:
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


# Streamlit UI
st.title('Movie Recommendation System')

selected_movie_name = st.selectbox("Choose the movie", options=movies['title'].values)

if st.button('Show Recommendation'):
    names, posters = recommend(selected_movie_name)
    cols = st.columns(5)
    for idx, col in enumerate(cols):
        col.text(names[idx])
        if posters[idx]:
            col.image(posters[idx])
