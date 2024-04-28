# Default target: start the stack
start:
	docker-compose up -d

# Stop the stack
stop:
	docker-compose down

# View logs
logs:
	docker-compose logs -f

# Build the load balancer container
build_lb:
	docker-compose build load_balancer

# Build the server container
build_server:
	docker-compose build server_container

# Rebuild the stack
rebuild: build_lb build_server start
