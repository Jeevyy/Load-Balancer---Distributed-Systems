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
        self.N = N
        self.K = K
        self.M = N * K
        self.hash_map = {i: [] for i in range(self.M)}  # Initialize hash_map as a dictionary of empty lists
        self.server_map = {}
        self.added_servers = {}
        self.removed_servers = []

    def hash_function(self, Rid):
        return Rid % self.M

    def server_hash_function(self, Sid):
    	if isinstance(Sid, int):
            return Sid % self.M
    	elif isinstance(Sid, str):
            # Convert string ID to hash
            hash_value = sum(ord(char) for char in Sid)
            return hash_value % self.M
    	else:
            raise TypeError("Server ID must be either integer or string.")


    def add_server(self, Sid):
        if Sid in self.server_map:
            return False #If server already exists

        for _ in range(self.K):
            hash_value = self.server_hash_function(Sid)
            while hash_value in self.server_map.values():
                Sid += 1
                hash_value = self.server_hash_function(Sid)
            self.hash_map[hash_value].append(Sid)
            server = Server(Sid)
            self.server_map[Sid] = server
            self.added_servers[Sid] = server
        return True

    def remove_server(self, Sid):
        if Sid not in self.server_map:
            print(f"{Sid} not found in server_map")
            return False

        hash_values_to_remove = []

        # Find hash values associated with the server to be removed
        for hash_value, server_list in self.hash_map.items():
            if Sid in server_list:
                hash_values_to_remove.append(hash_value)

        print("Hash values to remove:", hash_values_to_remove)

        # Remove the server from hash_map and server_map
        for hash_value in hash_values_to_remove:
            self.hash_map[hash_value].remove(Sid)

        print(f"Removed {Sid} from hash_map")

        self.server_map.pop(Sid)
        print(f"Removed {Sid} from server_map")

        return True

    def get_server(self, Rid):
        hash_value = self.hash_function(Rid)
        slots = len(self.hash_map)
        for i in range(slots):
            slot_index = (hash_value + i) % slots
            if self.hash_map[slot_index]:
                server_id = self.hash_map[slot_index][0]
                server = self.server_map[server_id]
                server.increment_request_count()
                return server_id  # Return the server ID
        return None

    def update_requests(self, server_id):
        if server_id is not None:
            server = self.server_map.get(server_id)
            if server:
                server.increment_request_count()


# Initialize Consistent Hash Map with N=5 and K=20 replicas per server
consistent_hash_map = ConsistentHashMap(N=8, K=3)

@app.route('/home')
def home():
    request_id = int(os.environ.get('REQUEST_ID', '0'))
    server_assigned = consistent_hash_map.get_server(request_id)
    if server_assigned is not None:
        consistent_hash_map.update_requests(server_assigned)  # This line is causing the error
        server = consistent_hash_map.server_map[server_assigned]
        return jsonify({"message": f"Hello from Server: {server.id}", "status": "successful", "servers": consistent_hash_map.hash_map}), 200
    else:
        return jsonify({"message": "No servers available", "status": "failed"}), 500


@app.route('/heartbeat')
def heartbeat():
    return '', 200


@app.route('/add_server', methods=['POST'])
def add_server():
    data = request.json
    num_instances = data.get('num_instances', 1)
    hostnames = data.get('hostnames', [])
    
    # Fill the remaining instances with automatically generated hostnames
    for i in range(num_instances - len(hostnames)):
        auto_hostname = f"Server_{len(consistent_hash_map.server_map) + 1}"
        hostnames.append(auto_hostname)

    for hostname in hostnames:
        success = consistent_hash_map.add_server(hostname)
        if not success:
            return jsonify({"message": f"Server {hostname} already exists", "status": "failed"}), 400
    
    return jsonify({"message": f"{num_instances} server(s) added successfully", "status": "successful"}), 200

@app.route('/remove_server', methods=['DELETE'])
def remove_server():
    data = request.json
    num_instances = data.get('num_instances', 1)
    hostnames = data.get('hostnames', [])

    if len(hostnames) > num_instances:
        return jsonify({"message": "Length of hostname list is more than removable instances", "status": "failure"}), 400

    removed_servers = []
    for hostname in hostnames:
        success = consistent_hash_map.remove_server(hostname)
        if success:
            removed_servers.append(hostname)

    if len(removed_servers) < num_instances:
        return jsonify({"message": "Could not remove all requested servers", "status": "failure"}), 400

    remaining_servers = list(consistent_hash_map.server_map.keys())

    response = {
        "message": {
            "N": len(remaining_servers),
            "replicas": remaining_servers
        },
        "status": "successful"
    }

    return jsonify(response), 200



@app.route('/view_changes')
def view_changes():
    return jsonify({"added_servers": consistent_hash_map.added_servers, "removed_servers": consistent_hash_map.removed_servers}), 200


@app.route('/rep', methods=['GET'])
def get_replicas():
    replicas = list(consistent_hash_map.server_map.keys())
    num_replicas = len(replicas)

    response = {
        "message": {
            "N": num_replicas,
            "replicas": replicas
         },
         "status": "successful"
     }
    return jsonify(response), 200

@app.route('/<path>', methods=['GET'])
def route_request(path):
    # Use consistent hashing algorithm to determine which server replica should handle the request for the given path
    server_replica = consistent_hashing_algorithm(path)

    # Check if the requested path is registered with any server replica
    if server_replica:
        # Forward the request to the appropriate server replica
        # Here you would make a request to the server replica to handle the path
        # You can use any HTTP client library like requests to make the request
        # Example: response = requests.get(f"http://{server_replica}/{path}")

        # For now, let's just simulate a successful response
        response_data = {"message": f"Request for {path} successfully routed to server replica {server_replica}", "status": "successful"}
        return jsonify(response_data), 200
    else:
        # Return an error response if the requested path is not registered with any server replica
        error_message = {"message": f"<Error> '{path}' endpoint does not exist in server replicas", "status": "failure"}
        return jsonify(error_message), 400


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)
