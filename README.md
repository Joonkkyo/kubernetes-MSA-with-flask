# kubernetes-MSA-with-flask
도커/쿠버네티스 온라인 부트캠프 with 카카오엔터프라이즈 최종과제

해당 문서에서는 UI 웹서버와 RestAPI 기반 flask 서버를 쿠버네티스 클러스터에서 MSA 방식으로 구축한 과정을 기술합니다.

# 1. UI Pod

MSA 방식으로 전환하기 위하여 github에 존재하는 website 폴더([https://github.com/DevenRathod2/simple-movie-website-html](https://github.com/DevenRathod2/simple-movie-website-html)) 에서 변경한 점에 대해 설명하도록 하겠습니다.

## 1. 폴더 구조 및 내용

![image](https://user-images.githubusercontent.com/12121282/150470118-8e69765d-312b-4a12-a2b3-f3830adf17e7.png)

![image](https://user-images.githubusercontent.com/12121282/150470158-6267875c-1c32-46e6-a8e7-da95487b84f7.png)

왼쪽이 기존 폴더의 구조이고, 오른쪽이 MSA 전환을 위하여 변경된 폴더 구조입니다. flask 서버를 기반으로 UI를 구동하기 위해 전반적인 폴더의 구조를 변경하고, 일부 파일을 추가하였습니다.

- static 폴더를 추가하고 스타일시트, 자바스트립트, 이미지 파일을 해당 폴더 내부로 이동시켜 정적 파일 참조를 쉽게 할 수 있도록 변경하였습니다.
- html 파일을 저장하는 templates 폴더를 생성하고 기존에 존재하는 html 파일을 해당 폴더로 이동시켰습니다.
- flask 서버 가동을 위한 `app.py` 파일을 생성하여 각각의 웹페이지에 대한 라우팅 처리와 RestAPI와의 통신을 할 수 있도록 구현하였습니다.

```python
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
    request = requests.get('http://172.30.6.154:31141/ns_movies/movies/' + title)
    response = request.text
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
```

RestAPI가 구동중인 서버에 GET method를 통해 요청을 보내 영화 정보를 받아옵니다. 영화 정보는 영화 제목, 감독, 개봉 년도, 상영 시간, 평점으로 구성되어 있습니다. 받아온 정보는 `movie_info.html` 에 인자 형태로 전달됩니다.

- 영화 정보를 저장하는 flask 서버로부터 데이터를 받아와서 표시하는 영화 정보 페이지 `movie_info.html` 를 추가하였습니다.

```html
<h1>Movie Information</h1>
<br><h3>영화 제목: {{title}}</h3>
<h3>영화 감독: {{director}}</h3>
<h3>개봉 년도: {{year}}</h3>
<h3>상영 시간: {{time}}</h3>
<h3>평점: {{rating}}</h3>
```

- `index.html` 에서 변경된 파일 구조에 부합하도록 이미지 파일 경로를 변경하고 URL을 RestAPI의 형식에 맞게 수정하였습니다.

```html
<div class="cards">
<a href="movies/Evil Dead"><div class="row">
  <div class="column nature">
    <div class="content">
      <img src="{{url_for('static', filename='img/1.jpg')}}" alt="Mountains">
      <h4>Evil Dead 2013</h4>
      
    </div>
    </a>
  </div>
  <a href="movies/Annabelle Creation">
  <div class="column nature">
    <div class="content">
      <img src="{{url_for('static', filename='img/2.jpg')}}" alt="Lights">
      <h4>Annabelle Creation (2017)</h4>
    </div>
  </div>
```

## 2. Dockerfile

해당 웹서버를 파드로 구성할 때 필요한 이미지를 빌드하기 위한 dockerfile을 작성하였습니다.

```docker
FROM python:3

WORKDIR /source

COPY . .

RUN apt-get update 
RUN pip install flask

EXPOSE 4000

CMD ["python", "app.py"]
```

flask 서버 구동에 필요한 python 모듈을 설치하고 포트 번호는 기존에 설정한 4000번과 일치시켰습니다. 그리고 `python app.py` 를 통해 파드 실행시 자동으로 웹서버가 구동될 수 있도록 설계하였습니다. `docker build` 명령을 통해 이미를 생성하고, dockerhub에 push하여 쿠버네티스 클러스터 내부의 yaml 파일이 해당 이미지를 인식할 수 있게 하였습니다.

## 3. yaml 파일

해당 이미지를 기반으로 하는 파드를 배포하기 위한 `ui-deploy.yaml` 파일을 작성하였습니다. 

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  creationTimestamp: null
  labels:
    app: ui-deploy
  name: ui-deploy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: ui-deploy
  strategy: {}
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: ui-deploy
    spec:
      containers:
      - image: jkseo50/ui:1.5
        name: ui
        ports:
        - containerPort: 4000
        resources: {}
status: {}
```

사용하고자 하는 이미지와 컨테이너포트를 입력한 뒤 `kubectl apply` 명령을 통해 deployment를 생성하였고, `kubectl expose` 명령을 바탕으로 외부에서 접근할 수 있도록 서비스를 생성하였습니다. 

```yaml
apiVersion: v1
kind: Service
metadata:
  creationTimestamp: "2022-01-19T10:50:15Z"
  labels:
    app: ui-deploy
  name: ui-svc
  namespace: default
  resourceVersion: "1436047"
  uid: 412ea785-c433-4982-92da-681845afa9fc
spec:
  clusterIP: 10.97.207.60
  clusterIPs:
  - 10.97.207.60
  externalTrafficPolicy: Cluster
  internalTrafficPolicy: Cluster
  ipFamilies:
  - IPv4
  ipFamilyPolicy: SingleStack
  ports:
  - nodePort: 30782
    port: 4000
    protocol: TCP
    targetPort: 4000
  selector:
    app: ui-deploy
  sessionAffinity: None
  type: NodePort
status:
  loadBalancer: {}
```

containerPort와 targetPort를 일치시켜 외부에서 접근 가능한 nodePort를 통해 웹서버에 정상적으로 접속할 수 있도록 서비스 내용을 수정하였습니다.

# 2. RestAPI Pod

## 1. 폴더 구조 및 내용

RestAPI 기반의 flask 서버를 구성하기 위한 폴더의 구조는 다음과 같습니다. 

![Untitled](MSA%20%E1%84%80%E1%85%AE%E1%84%8E%E1%85%AE%E1%86%A8%20%E1%84%87%E1%85%A9%E1%84%80%E1%85%A9%E1%84%89%E1%85%A5%20-%20%E1%84%89%E1%85%A5%E1%84%8C%E1%85%AE%E1%86%AB%E1%84%80%E1%85%AD%20bd50973a2f0946b687a81dc33aaee3e6/Untitled%202.png)

flask 서버 실행을 위한 `[app.py](http://app.py)` 파일과 이미지 빌드를 위한 Dockerfile로 구성하였습니다. `app.py` 파일의 내용은 다음과 같습니다.

```python
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
```

RestAPI 서버에서 두 가지의 url 패턴으로 라우팅을 진행하였습니다. `/movies` 를 통해 서버에 존재하는 영화의 개수와 영화 정보 데이터를 조회할 수 있고, `/movies/<title>` 를 통해 영화 정보에 대한 CRUD 작업을 수행하거나 특정 영화의 정보를 받아올 수 있도록 구현하였습니다. 영화 정보는 영화 제목, 영화 감독, 개봉 년도, 상영 시간, 평점으로 구성된 json 형태의 데이터로 구성하였습니다. 해당 서버는 3000번 포트를 통해 실행됩니다.

## 2. Dockerfile

```docker
FROM python:3

WORKDIR /source

COPY . .

RUN apt-get update
RUN pip install flask
RUN pip install flask_restx

EXPOSE 3000

CMD ["python", "app.py"]
```

UI 이미지를 빌드할 때 사용한 dockerfile과 동일한 방식으로 서버 구동에 필요한 모듈을 추가적으로 설치하고, 3000번 포트로 호스트와 연결할 포트를 설정하였습니다. `python app.py` 명령을 통해 파드 실행시에 자동으로 서버가 구동될 수 있도록 하였습니다. 이전과 마찬가지로 해당 dockerfile을 기반으로 이미지를 생성하였고, dockerhub에 push하였습니다.

## 3. yaml 파일

해당 이미지를 기반으로 하는 파드를 배포하기 위한 `movie-info-deploy.yaml` 파일을 작성하였습니다. 

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  creationTimestamp: null
  labels:
    app: movie-info-deploy
  name: movie-info-deploy
spec:
  replicas: 1
  selector:
    matchLabels:
      app: movie-info-deploy
  strategy: {}
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: movie-info-deploy
    spec:
      containers:
      - image: jkseo50/movie-info:1.1
        name: movie-info
        ports:
        - containerPort: 3000
        resources: {}
status: {}
```

dockerhub에 배포했던 RestAPI 서버 이미지 기반의 pod를 배포하기 위한 deployment를 생성합니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  creationTimestamp: "2022-01-19T10:41:37Z"
  labels:
    app: movie-info-deploy
  name: movie-info-svc
  namespace: default
  resourceVersion: "1434385"
  uid: ebd34234-9499-4094-9bb5-ead8d8ff9c82
spec:
  clusterIP: 10.108.251.244
  clusterIPs:
  - 10.108.251.244
  externalTrafficPolicy: Cluster
  internalTrafficPolicy: Cluster
  ipFamilies:
  - IPv4
  ipFamilyPolicy: SingleStack
  ports:
  - nodePort: 31141
    port: 3000
    protocol: TCP
    targetPort: 3000
  selector:
    app: movie-info-deploy
  sessionAffinity: None
  type: NodePort
status:
  loadBalancer: {}
```

이전과 마찬가지로 nodePort, targetPort를 수정하여 외부에서 접속할 수 있도록 합니다.

# 3. Kubernetes 배포 과정

- Deployment를 통한 Pod 배포

```docker
kubectl apply -f ui-deploy.yaml
kubectl apply -f movie-info-deploy.yaml
```

![image](https://user-images.githubusercontent.com/12121282/150470205-93b9e6c8-5fd0-4366-abad-d0fd0495409f.png)

- Service 생성

```docker
kubectl expose deployment ui-deploy --name ui-svc --type=NodePort
kubectl expose deployment movie-info-deploy --name movie-info-svc --type=NodePort
```

![image](https://user-images.githubusercontent.com/12121282/150470217-04e386fa-32d9-40d8-b3c0-c300835b2dd0.png)

# 4. 접속 결과

- 172.30.6.154:30782

![image](https://user-images.githubusercontent.com/12121282/150470260-3799d24d-18ab-4e10-ac9e-dde14d3f9a48.png)

- 172.30.6.154:31141

![image](https://user-images.githubusercontent.com/12121282/150470274-fb548adf-3fc2-46b3-9833-6aef9a9c9b2a.png)

