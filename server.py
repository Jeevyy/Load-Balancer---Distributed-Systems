from flask import Flask, jsonify, request
import os

app = Flask(__name__)

class ConsistentHashMap:
    def __init__(self, M):
        self.M = M  # Total number of slots in the consistent hash map
        self.hash_map = [[] for _ in range(M)]  # Initialize hash map with empty lists
        self.added_servers = []  # List to track added servers
        self.removed_servers = []  # List to track removed servers

    def hash_function(self, Rid):
        return Rid % self.M

    def server_hash_function(self, Sid):
        return Sid % self.M

    def add_server(self, Sid):
        hash_value = self.server_hash_function(Sid)
        self.hash_map[hash_value].append({"server_id": Sid, "requests": 0})  # Initialize requests to 0
        self.added_servers.append(Sid)

    def remove_server(self, Sid):
        hash_value = self.server_hash_function(Sid)
        if Sid in [server['server_id'] for server in self.hash_map[hash_value]]:
            self.hash_map[hash_value] = [server for server in self.hash_map[hash_value] if server['server_id'] != Sid]
            self.removed_servers.append(Sid)

    def get_server(self, Rid):
        hash_value = self.hash_function(Rid)
        slots = len(self.hash_map)
        for i in range(slots):
            slot_index = (hash_value + i) % slots
            if self.hash_map[slot_index]:
                return self.hash_map[slot_index][0]['server_id']  # Return the server ID
        return None

    def update_requests(self, server_id):
        for slot in self.hash_map:
            for server in slot:
                if server['server_id'] == server_id:
                    server['requests'] += 1
                    return

# Initialize Consistent Hash Map
consistent_hash_map = ConsistentHashMap(512)

@app.route('/home')
def home():
    request_id = int(os.environ.get('REQUEST_ID', '0'))  # Get request ID from environment variable
    server_assigned = consistent_hash_map.get_server(request_id)
    if server_assigned is not None:
        consistent_hash_map.update_requests(server_assigned)
        return jsonify({"message": f"Hello from Server: {server_assigned}", "status": "successful", "servers": consistent_hash_map.hash_map}), 200
    else:
        return jsonify({"message": "No servers available", "status": "failed"}), 500

@app.route('/heartbeat')
def heartbeat():
    return '', 200

@app.route('/add_server', methods=['POST'])
def add_server():
    data = request.json
    server_id = data.get('server_id')
    consistent_hash_map.add_server(server_id)
    return jsonify({"message": f"Server {server_id} added successfully", "status": "successful"}), 200

@app.route('/remove_server', methods=['POST'])
def remove_server():
    data = request.json
    server_id = data.get('server_id')
    consistent_hash_map.remove_server(server_id)
    return jsonify({"message": f"Server {server_id} removed successfully", "status": "successful"}), 200

@app.route('/view_changes')
def view_changes():
    return jsonify({"added_servers": consistent_hash_map.added_servers, "removed_servers": consistent_hash_map.removed_servers}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
