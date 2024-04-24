#!usr/bin/env python

from flask import Flask, jsonify

app = Flask(__name__)

#Server ID passed as environment variable
import os
SERVER_ID = os.getenv("SERVER_ID", "Unknown")

@app.route("/home", methods = ["GET"])
def home():
    return jsonify({"message": f"Hello from Server: {SERVER_ID}", "status": "successful"}), 200

@app.route("/heartbeat", methods = ["GET"])
def heartbeat():
    return "", 200

if __name__ == "__main__":
   app.run(debug = True, host = "0.0.0.0", port = 5000) 
