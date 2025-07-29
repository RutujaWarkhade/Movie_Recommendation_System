import numpy as np
import pandas as pd
import ast
import requests
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pickle
# Load datasets
movies = pd.read_csv("tmdb_5000_movies.csv")
credits = pd.read_csv("tmdb_5000_credits.csv")

# Merge datasets on title
movies = movies.merge(credits, on="title")

# Keep required columns
movies = movies[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]

# Drop null values
movies.dropna(inplace=True)

#  Data Cleaning and Feature Engineering 

# Convert JSON strings into lists of names
def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L   

movies['genres'] = movies['genres'].apply(convert)
movies['keywords'] = movies['keywords'].apply(convert)

# Get top 3 cast members
def convert3(obj):
    L = []
    counter = 0
    for i in ast.literal_eval(obj):
        if counter != 3:
            L.append(i['name'])
            counter += 1
        else:
            break
    return L   

movies['cast'] = movies['cast'].apply(convert3)

# Extract director from crew
def fetch_director(obj):
    L = []
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            L.append(i['name'])
            break
    return L

movies['crew'] = movies['crew'].apply(fetch_director)

# Split overview into words
movies['overview'] = movies['overview'].apply(lambda x: x.split())

# Remove spaces from multi-word tags
for feature in ['genres', 'keywords', 'cast', 'crew']:
    movies[feature] = movies[feature].apply(lambda x: [i.replace(" ", "") for i in x])

# Combine all tags into one column
movies['tags'] = movies['overview'] + movies['genres'] + movies['keywords'] + movies['cast'] + movies['crew']

# Create new DataFrame with only necessary columns
new_df = movies[['movie_id', 'title', 'tags']].copy()

# Convert list of tags to string
new_df.loc[:, 'tags'] = new_df['tags'].apply(lambda x: " ".join(x))
new_df.loc[:, 'tags'] = new_df['tags'].apply(lambda x: x.lower())

# Stemming
ps = PorterStemmer()

def stem(text):
    y = []
    for i in text.split():
        y.append(ps.stem(i))
    return " ".join(y)

new_df.loc[:, 'tags'] = new_df['tags'].apply(stem)

#  Vectorization and Similarity Computation 

cv = CountVectorizer(max_features=5000, stop_words='english')
vectors = cv.fit_transform(new_df['tags']).toarray()

similarity = cosine_similarity(vectors)

# Save processed data for use in app.py

pickle.dump(new_df, open('movie_data.pkl', 'wb'))
pickle.dump(similarity, open('similarity.pkl', 'wb'))

