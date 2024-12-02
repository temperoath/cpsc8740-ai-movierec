import pandas as pd
movies = pd.read_csv("10kmovies.csv")

movies = movies[["id", "title", "overview", "genre"]]

# Make Tags by combining overview and genre categories
movies["tags"] = movies["overview"] + movies["genre"]

# Now drop redundant overview and genre categories
new_data = movies.drop(columns=["overview", "genre"])

# Now convert tags into a vector with scikit learn
from sklearn.feature_extraction.text import CountVectorizer

cv=CountVectorizer(max_features=10000, stop_words="english")

vector=cv.fit_transform(new_data["tags"].values.astype("U")).toarray()

# Using Cosine Similarity
# Imported from Sklearn

from sklearn.metrics.pairwise import cosine_similarity
similarity = cosine_similarity(vector)

def recommend(movies):
    index = new_data[new_data["title"]==movies].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
    for i in distance[0:5]:
        print(new_data.iloc[i[0]].title)

# Test of function successful!
# Now that Cosine Similarity of the data is known, we can save and call for use
# I'll save as a pickle file - to save current program state, transfer for later use, and cache results
import pickle
import streamlit as st

pickle.dump(new_data, open("movies_list.pkl", "wb"))

pickle.dump(similarity, open("similarity.pkl", "wb"))

pickle.load(open("movies_list.pkl", "rb"))




