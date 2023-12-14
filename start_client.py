import socket

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
host = '127.0.0.1'  # Server's IP address
port = 12345       # Port to connect to
client_socket.connect((host, port))

# Authenticate with the server by sending the secret key
AUTH_KEY = "mysecretkey"
client_socket.send(AUTH_KEY.encode('utf-8'))

# Receive authentication resuexitlt from the server
auth_result = client_socket.recv(1024).decode('utf-8')

if auth_result == "authenticated":
    print("Authentication successful. You are connected to the server.")
else:
    print("Authentication failed. Closing the connection.")
    client_socket.close()
    exit(1)

# Send messages to the server
while True:
    message = input("Enter a message (or 'exit' to quit): ")
    if message == 'exit':
        break
    client_socket.send(message.encode('utf-8'))

# Close the client socket
client_socket.close()

