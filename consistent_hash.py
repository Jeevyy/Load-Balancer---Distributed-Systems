import hashlib

class ConsistantHash:
    def __init__(self):
        self.slots = 512
        self.k = 20
        self.consistant_hash = [0] * self.slots
        self.map = {}

    def h(self, i: int) -> int:
        return (i*i + 2*i + 17) % self.slots

    def fi(self, i: int, j: int) -> int:
        return (i*i + j*j + 2*j + 25) % self.slots

    def get_server_id(self, server: str) -> int:
        return int(hashlib.md5(server.encode()).hexdigest(), 16) % self.slots

    def build(self, server_list: set[str]):
        for server in server_list:
            self.add_server_to_hash(server)

    def get_server_from_request(self, request_id: int) -> str:
        req_pos = self.h(request_id)
        for i in range(self.slots):
            if self.consistant_hash[req_pos] != 0:
                return self.consistant_hash[req_pos]
            else:
                req_pos = (req_pos + 1) % self.slots
        return None

    def add_server_to_hash(self, server: str):
        server_id = self.get_server_id(server)
        for j in range(self.k):
            pos = self.fi(server_id, j)
            if self.consistant_hash[pos] == 0:
                self.consistant_hash[pos] = server
            else:
                original_pos = pos
                while self.consistant_hash[pos] != 0:
                    pos = (pos + 1) % self.slots
                    if pos == original_pos:
                        raise Exception("Hash table is full")
                self.consistant_hash[pos] = server
        self.map[server] = server_id

    def remove_server_from_hash(self, server: str, request_counts: dict):
        server_id = self.map[server]
        for i in range(self.slots):
            if self.consistant_hash[i] == server:
                self.consistant_hash[i] = 0
        del self.map[server]
        
        total_requests = request_counts.pop(server, 0)
        servers = list(self.map.keys())
        if servers:
            requests_per_server = total_requests // len(servers)
            for s in servers:
                request_counts[s] += requests_per_server
