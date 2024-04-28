from flask import Flask, jsonify, request
import os
import random
import string
import psutil

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
        self.total_requests = 0  # Total number of requests handled by the system

    def hash_function(self, Rid):
        # Adjusting the hash function for better load balancing
        hash_object = hashlib.sha256(str(Rid).encode())
        hash_hex = hash_object.hexdigest()
        hash_value = int(hash_hex, 16) % self.M
        return hash_value

    def server_hash_function(self, Sid):
        hash_values = []
        for i in range(self.K):  # Generate K virtual nodes for each server
            combined_id = str(Sid) + "_" + str(i)  # Combine server ID and counter
            hash_value = hash(combined_id) % self.M  # Hash the combined ID
            hash_values.append(hash_value)
        return hash_values

    def add_server(self, Sid):
        if Sid in self.server_map:
            return False  # Server already exists
        for hash_value in self.server_hash_function(Sid):
            while hash_value in self.server_map.values():  # Conflict resolution
                Sid += 1
                hash_values = self.server_hash_function(Sid)  # Re-generate hash values
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
        self.total_requests += 1  # Increment total requests counter
        hash_value = self.hash_function(Rid)
        slots = len(self.hash_map)
        selected_server = None
        min_requests = float('inf')

        # Iterate through the hash map to find the server with the least requests
        for i in range(slots):
            slot_index = (hash_value + i) % slots
            if self.hash_map[slot_index]:
                server_id = self.hash_map[slot_index][0]
                server = self.server_map[server_id]
                if server.request_count < min_requests:
                    min_requests = server.request_count
                    selected_server = server_id

        # If no server is found (which could happen if the server map is empty),
        # return None to handle the situation gracefully
        if selected_server is None:
            return None

        # Increment request count for the selected server
        self.server_map[selected_server].increment_request_count()
        return selected_server


    def get_all_servers(self):
        return list(self.server_map.keys())

# Initialize Consistent Hash Map with N=5 server containers and K=20 replicas per server
consistent_hash_map = ConsistentHashMap(N=50, K=50)

class LoadBalancer:
    def __init__(self):
        self.replicas = []

    # Update add_replica method to include server statistics
    def add_replica(self, hostname):
        server = Server(hostname)
        self.replicas.append(server)

    # Update remove_replica method to handle server removal
    def remove_replica(self, hostname):
        self.replicas = [replica for replica in self.replicas if replica.id != hostname]

    # Update get_replicas_status method to include server health status
    def get_replicas_status(self):
        status = []
        for server in self.replicas:
            server_status = {
                "id": server.id,
                "request_count": server.request_count,
                "cpu_usage": psutil.cpu_percent(),  # Get CPU usage
                "memory_usage": psutil.virtual_memory().percent  # Get memory usage
            }
            status.append(server_status)
        return status

    # Implement a dynamic load balancing algorithm to select the next server based on load
    def get_next_server(self):
        # Choose the server with the lowest CPU usage
        if len(self.replicas) == 0:
            return None
        elif len(self.replicas) == 1:
            return self.replicas[0].id
        else:
            min_cpu_server = min(self.replicas, key=lambda x: psutil.cpu_percent())
            return min_cpu_server.id

        
# Initialize Load Balancer
load_balancer = LoadBalancer()


@app.route('/home')
def home():
    request_id = random.randint(0, 1000)  # Generate a random request ID
    server_assigned = load_balancer.get_next_server()
    server = consistent_hash_map.server_map.get(server_assigned)
    if server:
        server.increment_request_count()
    return jsonify({"message": f"Hello from Server: {server_assigned}", "status": "successful"}), 200



# Route to view server stats
@app.route('/server_stats')
def server_stats():
    stats = {server_id: server.request_count for server_id, server in consistent_hash_map.server_map.items()}
    return jsonify(stats), 200


@app.route('/heartbeat')
def heartbeat():
    return '', 200

@app.route('/add_server', methods=['POST'])
def add_server():
    data = request.json
    server_id = data.get('server_id')
    success = consistent_hash_map.add_server(server_id)
    if success:
        load_balancer.add_replica(server_id)
        return jsonify({"message": f"Server {server_id} added successfully", "status": "successful"}), 200
    else:
        return jsonify({"message": f"Server {server_id} already exists", "status": "failed"}), 400

@app.route('/remove_server', methods=['POST'])
def remove_server():
    data = request.json
    server_id = data.get('server_id')
    success = consistent_hash_map.remove_server(server_id)
    if success:
        load_balancer.remove_replica(server_id)
        return jsonify({"message": f"Server {server_id} removed successfully", "status": "successful"}), 200
    else:
        return jsonify({"message": f"Server {server_id} not found", "status": "failed"}), 400

@app.route('/view_changes')
def view_changes():
    return jsonify({"added_servers": consistent_hash_map.added_servers.keys(), "removed_servers": consistent_hash_map.removed_servers}), 200


@app.route('/rep', methods=['GET'])
def get_replicas_status():
    response_data = {
        "message": {
            "N": len(load_balancer.replicas),
            "replicas": load_balancer.get_replicas_status()
        },
        "status": "successful"
    }
    return jsonify(response_data), 200

@app.route('/add', methods=['POST'])
def add_replicas():
    data = request.json
    n = data.get('n')
    hostnames = data.get('hostnames')

    # Check if the number of hostnames provided matches the specified number of instances
    if len(hostnames) != n:
        return jsonify({"message": "<Error> Length of hostname list is more than newly added instances", "status": "failure"}), 400

    # Check if any of the provided hostnames already exist in the replicas
    existing_replicas = load_balancer.get_replicas_status()
    for hostname in hostnames:
        if hostname in existing_replicas:
            return jsonify({"message": f"<Error> Replica {hostname} already exists", "status": "failure"}), 400

    # Add new replicas
    for hostname in hostnames:
        consistent_hash_map.add_server(hostname)
        load_balancer.add_replica(hostname)

    response_data = {
        "message": {
            "N": len(load_balancer.replicas),
            "replicas": load_balancer.get_replicas_status()
        },
        "status": "successful"
    }
    return jsonify(response_data), 200

@app.route('/rm', methods=['DELETE'])
def remove_replicas():
    data = request.json
    n = data.get('n')
    hostnames = data.get('hostnames')

    # Check if the number of hostnames provided matches the specified number of instances
    if len(hostnames) != n:
        return jsonify({"message": "<Error> Length of hostname list is more than instances to be removed", "status": "failure"}), 400

    # Remove replicas
    for hostname in hostnames:
        consistent_hash_map.remove_server(hostname)
        load_balancer.replicas = [replica for replica in load_balancer.replicas if replica.id != hostname]

    response_data = {
        "message": {
            "N": len(load_balancer.replicas),
            "replicas": load_balancer.get_replicas_status()
        },
        "status": "successful"
    }
    return jsonify(response_data), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
