import socket
import threading
from cgitb import handler

import Ping
import Ports

# Dictionary to store user data with user IDs as keys
USERS = {
    'user1': {'name': 'Alice', 'age': 30},
    'user2': {'name': 'Bob', 'age': 25},
    'user3': {'name': 'Charlie', 'age': 35},
}

# Server class to manage incoming client connections and handle client requests
class Server:
    def __init__(self, host='localhost', port=9999):
        # Initialize server with list to store connections and flag to stop server
        self.connections = []
        self.done = False
        # Create a TCP socket for the server
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind socket to specified host and port
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)  # Set socket to listen with a backlog of 5
        print(f'Server started on {host}:{port}')

    # Main loop to accept incoming connections
    def run(self):
        try:
            while not self.done:
                client, addr = self.server_socket.accept()  # Accept new connection
                handler = ConnectionHandler(client, self)  # Create a handler for client
                self.connections.append(handler)  # Add handler to list of connections
                threading.Thread(target=handler.run).start()  # Start handler in a new thread
                print(f'Client {addr} connected and added to connections')
        except Exception as e:
            self.shutdown()  # Shutdown server on error
            print(f"Server error: {e}")

    # Adds a new user to USERS dictionary
    def post(self, user_name, user_age):
        USERS[f'user{len(USERS) + 1}'] = {'name': user_name, 'age': user_age}
        return "HTTP/1.1 200 OK\n\nUser data updated"

    # Retrieves a user's information from USERS
    def get(self, user_id):
        if user_id in USERS:
            return f"HTTP/1.1 200 OK\nContent-Type: application/json\n\n{USERS[user_id]}"
        else:
            return "HTTP/1.1 404 Not Found\n\nUser not found"

    # Closes all client connections and shuts down the server
    def shutdown(self):
        self.done = True
        self.server_socket.close()
        for handler in self.connections:
            handler.shutdown()
        print("Server shut down")


# Class to handle individual client connection
class ConnectionHandler:
    def __init__(self, client_socket, server):
        self.client_socket = client_socket
        self.server = server
        self.connected = True
        self.ID = None

    # Main loop to handle commands sent by the client
    def run(self):
        try:
            # Initial messages to prompt the user for a username and age
            self.client_socket.sendall(b'Welcome\nWhat is your username?\n')
            name = self.client_socket.recv(1024).decode().strip()
            self.client_socket.sendall(b'How old are you?\n')
            age = self.client_socket.recv(1024).decode().strip()

            # Validate age input to ensure it is an integer
            flag = False
            while not flag:
                try:
                    int(age)
                    flag = True
                except ValueError:
                    self.client_socket.sendall(b'How old are you?!!\n')
                    age = self.client_socket.recv(1024).decode().strip()

            # Save user ID after successful input
            self.ID = self.server.post(name, age)
            print(f"{name} connected!")

            # Print available commands on start
            self.send_message(f"\nHi {name}:)")
            self.send_message(command_help())

            # Loop to process incoming commands from the client
            while self.connected:
                message = self.client_socket.recv(1024).decode().strip()
                command_parts = message.split(" ")
                command = command_parts[0]
                parameters = command_parts[1:]

                # Command to exit the session
                if command.lower() == '/exit':
                    self.shutdown()


                # Command to retrieve user data
                elif command.lower().startswith("/get"):
                    if len(parameters) == 1:
                        print(f"{self.ID}: {message}")
                        self.send_message(self.server.get(parameters[0]))
                    else:
                        self.send_message("Usage: /GET <user_ID>")

                # Command to add new user data
                elif command.lower().startswith("/post"):
                    if len(parameters) == 2:
                        print(f"{self.ID}: {message}")
                        self.send_message(self.server.post(name, age))
                    else:
                        self.send_message("Usage: /POST <user_name> <user_age>")

                # Default message for unknown command
                else:
                    self.send_message(command_help())

        except Exception as e:
            print(f"ConnectionHandler error: {e}")
            self.shutdown()

    # Sends a message to the client
    def send_message(self, message):
        try:
            self.client_socket.sendall(f"{message}\n".encode())
        except Exception as e:
            print(f"Send message error: {e}")

    # Closes the client connection and removes user from USERS
    def shutdown(self):
        self.connected = False
        if self.ID in self.server.USERS:
            del self.server.USERS[self.ID]
            print(self.ID + " disconnected!")
        try:
            self.client_socket.close()
        except Exception as e:
            print(f"Shutdown error: {e}")


# Function to print available commands for the user
def command_help():
    return (
        "\n---------Command lines----------\n"
        "/help\n"
        "/ping <hostname/IP>\n"
        "/port <hostname/IP> <start_port> <end_port> <#num_requests>\n"
        "/res_time <hostname/IP> <port> <#num_requests>\n"
        "/GET <user_ID>\n"
        "/POST <user_name> <user_age>\n"
        "/exit\n"
        "'#' means you can send nothing:)\n"
        "--------------------------------------\n"
    )


if __name__ == '__main__':
    server = Server()
    try:
        server.run()  # Start the server
    except KeyboardInterrupt:
        server.shutdown()  # Shutdown the server on interrupt
