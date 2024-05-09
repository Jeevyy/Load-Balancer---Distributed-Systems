#!usr/bin/env python
#This line imports the Flask class and the jsonify function from the Flask library.
from flask import Flask, jsonify

#This line creates a new instance of the Flask class, which represents the Flask web application. The __name__ parameter is a Python variable that represents the name of the current module or script.
app = Flask(__name__)

#Server ID passed as environment variable
import os
SERVER_ID = os.getenv("SERVER_ID", "Unknown")

#This is a Flask route decorator that maps the /home URL to the home function. The methods=["GET"] parameter specifies that this route should only respond to HTTP GET requests. 
#The home function returns a JSON response with the message "Hello from Server: [SERVER_ID]" and a status of "successful". The jsonify function is used to convert the Python dictionary to a JSON string, and the 200 status code indicates a successful HTTP response.
@app.route("/home", methods = ["GET"])
def home():
    return jsonify({"message": f"Hello from Server: {SERVER_ID}", "status": "successful"}), 200

#This is another Flask route decorator that maps the /heartbeat URL to the heartbeat function. 
#The heartbeat function returns an empty string and a 200 status code, indicating a successful heartbeat response
@app.route("/heartbeat", methods = ["GET"])
def heartbeat():
    return "", 200

if __name__ == "__main__":
   app.run(debug = True, host = "0.0.0.0", port = 5000) 
