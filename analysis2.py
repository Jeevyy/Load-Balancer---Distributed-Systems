import asyncio
import aiohttp
import matplotlib.pyplot as plt
import json

async def send_request(session, url):
    async with session.get(url) as response:
        return await response.text()

async def send_requests(url, total_requests):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for _ in range(total_requests):
            task = asyncio.create_task(send_request(session, url))
            tasks.append(task)
        responses = await asyncio.gather(*tasks)
        return responses

async def main(num_servers, total_requests):
    url = 'http://localhost:6000/home'
    response_counts = {"server_" + str(i): 0 for i in range(1, num_servers + 1)}
    responses = await send_requests(url, total_requests)
    for response in responses:
        data = json.loads(response)
        server = data["message"].split(": ")[1]
        response_counts[server] += 1
    return response_counts


async def run_experiment(num_servers, total_requests):
    results = await main(num_servers, total_requests)
    avg_load = sum(results.values()) / len(results)
    return avg_load

async def run_experiments():
    num_servers_list = [2, 3, 4, 5, 6]
    total_requests = 10000
    avg_loads = []
    for num_servers in num_servers_list:
        avg_load = await run_experiment(num_servers, total_requests)
        avg_loads.append(avg_load)
    return num_servers_list, avg_loads

async def plot_graph():
    num_servers_list, avg_loads = await run_experiments()
    plt.plot(num_servers_list, avg_loads, marker='o')
    plt.xlabel('Number of Server Instances')
    plt.ylabel('Average Load')
    plt.title('Average Load of Servers vs. Number of Server Instances')
    plt.grid(True)
    plt.show()

if __name__ == "__main__":
    asyncio.run(plot_graph())

