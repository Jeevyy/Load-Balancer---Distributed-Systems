# Use the official Python image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY server.py /app

# Install Flask
RUN pip install --no-cache-dir Flask

# Expose port 6000 to the outside world
EXPOSE 6000

# Run server.py when the container launches
CMD ["python", "server.py"]
