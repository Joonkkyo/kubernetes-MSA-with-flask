FROM python:3

# set a directory for the app
WORKDIR /source

# copy all the files to the container
COPY . .

RUN apt-get update 
RUN pip install flask

# port number
EXPOSE 4000

# run command
CMD ["python", "app.py"]