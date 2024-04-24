# Use official Python runtime as a parent image
FROM python:3.9

#Set the working directory in the container
WORKDIR /app

#Copy the current directory contenst into container at /app
COPY server.py /app

#Install Flask
RUN pip install Flask

#Set SERVER_ID env variable
ENV SERVER_ID "1"

#Run app.py when container launches
CMD ["python", "server.py"]
