import asyncio
import aiohttp
import json
import matplotlib.pyplot as plt


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


async def main():
    url = 'http://localhost:6000/home'
    total_requests = 10000
    response_counts = {'server_1': 0, 'server_2': 0, 'server_3': 0}

    responses = await send_requests(url, total_requests)
    for response in responses:
        try:
            response_json = json.loads(response)
            server = response_json.get('message').split(': ')[1]
            response_counts[server] += 1
        except Exception as e:
            print(f"Error processing response: {e}")
            print(f"Response: {response}")

    print("Request counts handled by each server:")
    for server, count in response_counts.items():
        print(f"{server}: {count}")

    # Plot the bar graph
    servers = list(response_counts.keys())
    counts = list(response_counts.values())
    plt.bar(servers, counts)
    plt.xlabel('Server')
    plt.ylabel('Request Count')
    plt.title('Request counts handled by each server')
    plt.show()


if __name__ == "__main__":
    asyncio.run(main())


