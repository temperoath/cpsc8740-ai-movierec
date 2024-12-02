import streamlit as st
import pickle
import requests
import time
import subprocess

# Flag to track if subprocess has run
subprocess_run = False

def generate_pickle_files():
    global subprocess_run
    # Check if subprocess has already run
    if not subprocess_run:
        # Run the subprocess (main.py) to generate pickle files
        subprocess.run(['python', 'main.py'])
        subprocess_run = True  # Set flag to True

# Try loading pickle files
try:
    # Load data (pickle file) created by back-end main.py
    movies = pickle.load(open("movies_list.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    movies_list = movies["title"].values
except FileNotFoundError:
    # If pickle files don't exist, generate them
    generate_pickle_files()
    # Retry loading after generation
    movies = pickle.load(open("movies_list.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))
    movies_list = movies["title"].values

# Display header and select box
st.title("Movie Recommendation System")
st.divider()
st.subheader("What is your favorite movie?", divider = "red")
def reset_recommendations():
    """Reset recommendations and index when a new movie is selected."""
    st.session_state["recommendations"] = None
    st.session_state["current_index"] = 0

selectvalue = st.selectbox("Please select a movie",movies_list, on_change=reset_recommendations)

def fetch_poster_and_overview(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=62a330265dc4a543db69dc692ab09e75"
    response = requests.get(url)
    data = response.json()

    poster_url = "https://via.placeholder.com/500x750?text=No+Poster+Available"
    overview = "No Overview Available"

    if 'poster_path' in data and data['poster_path']:
        poster_url = "https://image.tmdb.org/t/p/w500/" + data['poster_path']

    if 'overview' in data and data['overview']:
        overview = data['overview']
    return poster_url, overview

# Define recommendation function
def recommend(movie):
    index = movies[movies["title"] == movie].index[0]
    if index < len(similarity):  # Check if index is within bounds
        distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
        recommend_movie = []
        recommend_poster = []
        recommend_overview = []
        for i in distance[1:6]:
            movies_id = movies.iloc[i[0]].id
            recommend_movie.append(movies.iloc[i[0]].title)
            poster_url, overview = fetch_poster_and_overview(movies_id)
            recommend_poster.append(poster_url)
            recommend_overview.append(overview)

        return recommend_movie, recommend_poster, recommend_overview
    else:
        return []  # If the index is out of range, return an empty list

# Get movie recommendations
previous_recommendations = None
movie_name, movie_poster, movie_overview = recommend(selectvalue)

# Initialize session state for recommendation storage
if "recommendations" not in st.session_state:
    st.session_state["recommendations"] = None
if "current_index" not in st.session_state:
    st.session_state["current_index"] = 0

def increment_index():
    """Move to the next recommendation."""
    st.session_state["current_index"] += 1
    if st.session_state["current_index"] >= len(st.session_state["recommendations"][0]):
        st.session_state["current_index"] = 0  # Loop back to the first recommendation

def decrement_index():
    """Move to the previous recommendation."""
    st.session_state["current_index"] -= 1
    if st.session_state["current_index"] < 0:
        st.session_state["current_index"] = len(st.session_state["recommendations"][0]) - 1  # Loop to the last recommendation

# Display recommendations when button is clicked
if st.button("Show Recommendations"):
    with st.spinner("Generating Recommendations!"):
        time.sleep(2)

        # Generate recommendations only if not already done
        if st.session_state["recommendations"] is None:
            movie_name, movie_poster, movie_overview = recommend(selectvalue)
            st.session_state["recommendations"] = (movie_name, movie_poster, movie_overview)

# Display the current recommendation if recommendations are available
if st.session_state["recommendations"]:
    # Extract recommendations from session state
    movie_name, movie_poster, movie_overview = st.session_state["recommendations"]
    current_index = st.session_state["current_index"]

    # Display the current recommendation
    st.subheader(movie_name[current_index])
    st.image(movie_poster[current_index])
    st.text(movie_overview[current_index])

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("⬅️ Previous", key="prev"):
            decrement_index()
    with col3:
        if st.button("Next ➡️", key="next"):
            increment_index()

