from flask import Flask, render_template
import requests
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/movies/<title>')
def movie(title):
    requestData = requests.get('http://172.30.6.154:31141/ns_movies/movies/' + title)
    response = requestData.text
    movie_info = json.loads(response)
    title = movie_info['data']['title']
    director = movie_info['data']['director']
    year = movie_info['data']['release_year']
    time = movie_info['data']['running_time']
    rating = movie_info['data']['rating']

    return render_template('movie_info.html', 
                            title=title, 
                            director=director,
                            year=year,
                            time=time,
                            rating=rating)
    

if __name__ == "__main__":
    app.run(host='0.0.0.0', port="4000", debug=True)