import socket
import threading
import sys


# Client class to manage connection and handle communication with the server
class Client:
    def __init__(self, host='127.0.0.1', port=9999):
        # Initialize client socket and connect to the specified server
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        self.done = False  # Flag to indicate if the client should stop

    # Main method to start the client
    def run(self):
        try:
            # Start a separate thread to handle user input
            input_handler = threading.Thread(target=self.input_handler)
            input_handler.start()

            # Listen for messages from the server
            while not self.done:
                try:
                    # Receive and decode message from server
                    in_message = self.client_socket.recv(1024).decode()
                    if not in_message:
                        break
                    else:
                        print(in_message)  # Print received message
                except Exception as e:
                    print(f"Error receiving message: {e}")
                    self.shutdown()  # Shutdown on error

        except Exception as e:
            print(f"Connection error: {e}")
            self.shutdown()

    # Method to handle user input and send commands to the server
    def input_handler(self):
        try:
            while not self.done:
                # Read input from the user
                message = input()
                command_parts = message.split(" ")
                command = command_parts[0]
                parameters = command_parts[1:]
                int_inputs = parameters[1:]  # Parameters that should be integers

                # Check command and send appropriate message to server
                if command.lower() == '/exit':
                    self.client_socket.sendall(message.encode())
                    self.shutdown()

                # Command to ping a host
                elif command.lower().startswith("/ping"):
                    if len(parameters) == 1:
                        self.client_socket.sendall(message.encode())
                    else:
                        print("Usage: /ping <hostname/IP>")


                # Command to retrieve user information
                elif command.lower().startswith("/get"):
                    if len(parameters) == 1:
                        self.client_socket.sendall(message.encode())
                    else:
                        print("Usage: /GET <user_ID>")

                # Command to add new user information
                elif command.lower().startswith("/post"):
                    if len(parameters) == 2:
                        self.int_checker(int_inputs, message)  # Validate integer inputs
                    else:
                        print("Usage: /POST <user_name> <user_age>")

                # Send other commands directly to the server
                else:
                    self.client_socket.sendall(message.encode())

        except Exception as e:
            print(f"Input handler error: {e}")
            self.shutdown()

    # Method to close the client socket and stop the client
    def shutdown(self):
        self.done = True
        try:
            self.client_socket.close()
            print("Client shut down")
            sys.exit(0)  # Exit cleanly
        except Exception as e:
            print(f"Shutdown error: {e}")
            sys.exit(1)

    # Method to check if specific parameters are integers
    def int_checker(self, parameters, message):
        try:
            for parameter in parameters:
                int(parameter)  # Convert each parameter to integer
            self.client_socket.sendall(message.encode())  # Send message if all are valid integers
        except ValueError:
            print("Invalid input.")  # Notify user if any parameter is not an integer


# Entry point to start the client
if __name__ == '__main__':
    client = Client()
    try:
        client.run()  # Start client
    except KeyboardInterrupt:
        client.shutdown()  # Shutdown client on interrupt
