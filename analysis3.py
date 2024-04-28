import unittest
import requests

class TestLoadBalancer(unittest.TestCase):
    def test_home_endpoint(self):
        #Test case for /home endpoint
        response = requests.get('http://localhost:6000/home')
        self.assertEqual(response.status_code, 200)
     
    def test_add_server_endpoint(self):
        #Test case for /add_server endpoint
        response = requests.post("http://localhost:6000/add_server", json={'num_instances': 1, 'hostnames': ['server_1']})
        self.assertEqual(response.status_code, 200)

    def test_remove_server_endpoint(self):
        #Test case for /remove_server endpoint
        response = requests.delete('http://localhost:6000/remove_server', json={'num_instances': 1, 'hostnames': ['server_1']})
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
   unittest.main()

