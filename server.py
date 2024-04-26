from flask import Flask, jsonify, request
import os

app = Flask(__name__)

class Server:
    def __init__(self, server_id):
        self.id = server_id
        self.request_count = 0

    def increment_request_count(self):
        self.request_count += 1

class ConsistentHashMap:
    def __init__(self, N, K):
        self.N = N  # Total number of server containers
        self.K = K  # Number of times each server is replicated
        self.M = N * K  # Total number of slots in the consistent hash map
        self.hash_map = [[] for _ in range(self.M)]  # Initialize hash map with empty lists
        self.server_map = {}  # Dictionary to map server IDs to slots
        self.added_servers = {}  # Dictionary to track added servers
        self.removed_servers = []  # List to track removed servers

    def hash_function(self, Rid):
        return Rid % self.M

    def server_hash_function(self, Sid):
        return Sid % self.M

    def add_server(self, Sid):
        if Sid in self.server_map:
            return False  # Server already exists
        for _ in range(self.K):
            hash_value = self.server_hash_function(Sid)
            while hash_value in self.server_map.values():  # Conflict resolution
                Sid += 1
                hash_value = self.server_hash_function(Sid)
            self.hash_map[hash_value].append(Sid)
            server = Server(Sid)
            self.server_map[Sid] = server
            self.added_servers[Sid] = server
        return True

    def remove_server(self, Sid):
        if Sid not in self.server_map:
            return False  # Server not found
        for _ in range(self.K):
            hash_value = self.server_map.pop(Sid).id
            self.hash_map[hash_value].remove(Sid)
            self.removed_servers.append(Sid)
        return True

    def get_server(self, Rid):
        hash_value = self.hash_function(Rid)
        slots = len(self.hash_map)
        for i in range(slots):
            slot_index = (hash_value + i) % slots
            if self.hash_map[slot_index]:
                server_id = self.hash_map[slot_index][0]
                server = self.server_map[server_id]
                server.increment_request_count()  # Increment request count for the selected server
                return server_id  # Return the server ID
        return None

# Initialize Consistent Hash Map with N=5 server containers and K=20 replicas per server
consistent_hash_map = ConsistentHashMap(N=5, K=20)

@app.route('/home')
def home():
    request_id = int(os.environ.get('REQUEST_ID', '0'))  # Get request ID from environment variable
    server_assigned = consistent_hash_map.get_server(request_id)
    return jsonify({"message": f"Hello from Server: {server_assigned}", "status": "successful"}), 200

@app.route('/heartbeat')
def heartbeat():
    return '', 200

@app.route('/add_server', methods=['POST'])
def add_server():
    data = request.json
    server_id = data.get('server_id')
    success = consistent_hash_map.add_server(server_id)
    if success:
        return jsonify({"message": f"Server {server_id} added successfully", "status": "successful"}), 200
    else:
        return jsonify({"message": f"Server {server_id} already exists", "status": "failed"}), 400

@app.route('/remove_server', methods=['POST'])
def remove_server():
    data = request.json
    server_id = data.get('server_id')
    success = consistent_hash_map.remove_server(server_id)
    if success:
        return jsonify({"message": f"Server {server_id} removed successfully", "status": "successful"}), 200
    else:
        return jsonify({"message": f"Server {server_id} not found", "status": "failed"}), 400

@app.route('/view_changes')
def view_changes():
    return jsonify({"added_servers": consistent_hash_map.added_servers.keys(), "removed_servers": consistent_hash_map.removed_servers}), 200

@app.route('/server_stats')
def server_stats():
    stats = {server_id: server.request_count for server_id, server in consistent_hash_map.added_servers.items()}
    return jsonify(stats), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
