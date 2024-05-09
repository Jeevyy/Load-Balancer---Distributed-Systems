# Load-Balancer - Distributed-Systems
### This repository contains the implementation of a load balancer using Docker, aimed at efficiently distributing requests among several servers. The load balancer routes requests from multiple clients asynchronously to ensure nearly even distribution of the load across the server replicas.

Basic Task Overview
Task 1: Server
Task 2: Consistent Hashing
Task 3: Load Balancer
Task 4: Analysis

## Task Description
### Task One
1. Implement a load balancer that routes requests among several servers asynchronously.
2. Use Docker to manage the deployment of the load balancer and servers within a Docker network.
3. Implement a simple web server in Python to handle HTTP requests on specified endpoints (/home and /heartbeat).
   -`/home` (GET): Returns a string with a unique identifier to distinguish among replicated server containers.
   - `/heartbeat` (GET): Sends a heartbeat response for failure detection by the load balancer.
4. Use consistent hashing data structure for efficient request distribution.
5. Ensure fault tolerance by spawning new replicas of servers in case of failures
6. Test and analyze the performance of the load balancer implementation in different scenarios.
     -Report observations and explanations for the following experiments:
     -Distribution of 10,000 async requests among N=3 server containers.
     -Average load on servers as N is incremented from 2 to 6 with 10,000 requests.
     -Load balancer's behavior in case of server failure.
     - Observations after modifying the hash functions.
7. Write clean and well-documented code, along with a README file detailing design choices, assumptions, testing, and performance analysis.
8. Provide a Makefile for deploying and running the code, and version control the project using Git.

## Group Members
1. 137991 - Jesse Kamau
2. 144914 - Aman Vasani
3. 138216 - Sylvester Letting
4. 146254 - Jeevan Sehmi

