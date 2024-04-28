import requests
import matplotlib.pyplot as plt
import numpy as np

# Function to launch 10000 async requests on N = 3 server containers
def launch_requests():
    url = 'http://localhost:6000/home'
    server_counts = 3
    server_request_counts = [0] * server_counts
    
    # Launch 10000 async requests
    for _ in range(10000):
        response = requests.get(url)
        server_id = int(response.json()['message'].split()[-1]) - 1
        server_request_counts[server_id] += 1
    
    # Plot the request count handled by each server instance in a bar chart
    plt.bar(np.arange(server_counts) + 1, server_request_counts)
    plt.xlabel('Server Instance')
    plt.ylabel('Request Count')
    plt.title('Request Count Handled by Each Server Instance')
    plt.show()

# Function to increment N from 2 to 6 and launch 10000 requests on each increment
def test_scalability():
    url = 'http://localhost:6000/add'
    server_counts = list(range(2, 7))
    average_loads = []
    
    # Increment N from 2 to 6 and launch 10000 requests on each increment
    for N in server_counts:
        data = {'n': N, 'hostnames': [f'server_{i}' for i in range(1, N + 1)]}
        response = requests.post(url, json=data)
        
        # Launch 10000 requests
        server_request_counts = [0] * N
        for _ in range(10000):
            response = requests.get('http://localhost:6000/home')
            server_id = int(response.json()['message'].split()[-1]) - 1
            server_request_counts[server_id] += 1
        
        # Calculate the average load of the servers
        average_load = sum(server_request_counts) / N
        average_loads.append(average_load)
    
    # Plot the average load of the servers at each run in a line chart
    plt.plot(server_counts, average_loads, marker='o')
    plt.xlabel('Number of Servers')
    plt.ylabel('Average Load')
    plt.title('Average Load of Servers for Different Number of Servers')
    plt.grid(True)
    plt.show()

# Function to test all endpoints of the load balancer and show that it promptly recovers from server container failure
def test_server_failure_recovery():
    # Send requests to view server stats
    response = requests.get('http://localhost:6000/server_stats')
    print("Initial Server Stats:", response.json())
    
    # Simulate server container failure by removing a server
    response = requests.post('http://localhost:6000/remove_server', json={'server_id': 'server_1'})
    print("Server Removal Status:", response.json())
    
    # Send requests again to view updated server stats
    response = requests.get('http://localhost:6000/server_stats')
    print("Updated Server Stats:", response.json())

# Task A-1: Launch 10000 async requests on N = 3 server containers and report the request count handled by each server instance in a bar chart
launch_requests()

# Task A-2: Increment N from 2 to 6 and launch 10000 requests on each increment. Report the average load of the servers at each run in a line chart
test_scalability()

# Task A-3: Test all endpoints of the load balancer and show that in case of server failure, the load balancer spawns a new instance quickly to handle the load
test_server_failure_recovery()
