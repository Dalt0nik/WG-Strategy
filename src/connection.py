import socket
from urllib.parse import urlparse

class ServerConnection:
    def __init__(self, server_website, server_port):
        self.server_address = self.get_server_ip(server_website)
        self.server_port = server_port
        self.client_socket = self.create_socket()

    def create_socket(self):
        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        return client_socket

    def connect(self):
        try:
            # Connect to the server
            self.client_socket.connect((self.server_address, self.server_port))
            print("Connected to server")
        except ConnectionRefusedError:
            print("Connection refused. Make sure the server is running and reachable.")

    def get_server_ip(self, server_website):
        # Parse the URL to extract the hostname
        parsed_url = urlparse(server_website)
        hostname = parsed_url.hostname
        
        # Resolve the hostname to an IP address
        ip_address = socket.gethostbyname(hostname)
        
        return ip_address

    def send_request(self, request):
        try:
            # Send the request
            self.client_socket.sendall(request)
            data = self.client_socket.recv(2048)
            return data
        except Exception as e:
            print("An error occurred while sending the request:", e)
            return None

    def close(self):
        # Close the socket
        self.client_socket.close()

