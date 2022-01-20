FROM python:3

# set a directory for the app
WORKDIR /source

# copy all the files to the container
COPY . .

RUN apt-get update
RUN pip install flask
RUN pip install flask_restx
# port number
EXPOSE 3000

# run command
CMD ["python", "app.py"]
~                        