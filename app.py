from flask import Flask, render_template, request
import pickle
import requests
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("TMDB_API_KEY")

app = Flask(__name__)

movies = pickle.load(open('movie_data.pkl', 'rb'))
similarity = pickle.load(open('similarity.pkl', 'rb'))

def fetch_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}&language=en-US"
    response = requests.get(url)
    data = response.json()
    poster_path = data.get('poster_path')
    if poster_path:
        return f"https://image.tmdb.org/t/p/w500/{poster_path}"
    return "https://via.placeholder.com/500x750.png?text=No+Poster"

def recommend(movie):
    try:
        index = movies[movies['title'] == movie].index[0]
    except IndexError:
        return [], []

    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])[1:6]
    recommended_titles = []
    recommended_posters = []

    for i in distances:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_titles.append(movies.iloc[i[0]].title)
        recommended_posters.append(fetch_poster(movie_id))

    return recommended_titles, recommended_posters

@app.route('/', methods=['GET', 'POST'])
def index():
    recommended_movies = []
    if request.method == 'POST':
        movie_input = request.form.get('selected_movie') or request.form.get('manual_movie')
        recommended_titles, recommended_posters = recommend(movie_input)
        recommended_movies = zip(recommended_titles, recommended_posters)
        return render_template('recommend.html', movie=movie_input, recommended_movies=recommended_movies)

    return render_template('index.html', movie_list=movies['title'].values)

@app.route('/recommend', methods=['POST'])
def recommend_route():
    return index()

if __name__ == "__main__":
    app.run(debug=True)
