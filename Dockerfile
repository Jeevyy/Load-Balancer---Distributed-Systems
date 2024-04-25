# Use official Python runtime as a parent image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY server.py /app

# Install Flask
RUN pip install Flask

# Set SERVER_ID environment variable
ENV SERVER_ID="1"

# Expose port 6000
EXPOSE 6000

# Run server.py when the container launches
CMD ["python", "server.py"]
