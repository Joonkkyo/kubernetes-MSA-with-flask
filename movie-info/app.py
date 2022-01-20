from flask import Flask, request, Response
from flask_restx import Resource, Api, fields
from flask import abort


app = Flask(__name__)
api = Api(app)

ns_movies = api.namespace('ns_movies', description='Movie APIs')

movie_data = api.model(
    'Movie Data',
    {
      "title": fields.String(description="movie title", required=True),
      "director": fields.String(description="movie director", required=True),
      "release_year": fields.String(description="release year", required=True),
      "running_time": fields.String(description="running time", required=True),
      "rating": fields.String(description="IMDb Rating", required=True)
    }
)

movie_info = {}
number_of_movies = 0

@ns_movies.route('/movies')
class movies(Resource):
    def get(self):
        return {
            'number_of_movies': number_of_movies,
            'movie_info': movie_info
        }

@ns_movies.route('/movies/<string:title>')
class movie_title(Resource):
    # 영화 정보 조회
    def get(self, title):
        if not title in movie_info.keys():
            abort(404, description=f"Title {title} doesn't exist")
        data = movie_info[title]

        return {'data': data}

    @api.expect(movie_data)
    def post(self, title): 
        if title in movie_info.keys():
            abort(404, description=f"Title {title} already exists")
        
        params = request.get_json()
        movie_info[title] = params
        global number_of_movies
        number_of_movies += 1

        return Response(status=200)
        
    def delete(self, title):
        if not title in movie_info.keys():
            abort(404, description=f"Title {title} doesn't exist")
        
        del movie_info[title]
        global number_of_movies
        number_of_movies -= 1

        return Response(status=200)

    @api.expect(movie_data)
    def put(self, title):
        global movie_info

        if not title in movie_info.keys():
            abort(404, description=f"Title {title} doesn't exist")
        
        params = request.get_json()
        movie_info[title] = params

        return Response(status=200)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)
