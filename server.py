import socket
import threading

clientInfo = {}

# Define a secret authentication key
AUTH_KEY = "mysecretkey"

def authenticate(client_socket):
    # Receive the authentication key from the client
    auth_message = client_socket.recv(1024).decode('utf-8')

    # Check if the received key matches the predefined key
    if auth_message == AUTH_KEY:
        return True
    else:
        return False
    

def client_thread(client_socket, addr):
    if clientInfo.get(addr[0]) == None:
        clientInfo[addr[0]] = 0
    print(f"Connected to {addr}")

    valid = True
    # Authenticate the client
    if not authenticate(client_socket):
        print("Authentication failed. Closing the connection.")
        client_socket.send("authentication failed".encode('utf-8'))  # Notify the client
        client_socket.close()
        valid = False
    else:
        client_socket.send("authenticated".encode('utf-8'))  # Notify the client

    # Receive and print messages from the authenticated client
    
    while valid:
        message = client_socket.recv(1024)
        if not message:
            break
        clientInfo[addr[0]] += 1
        print(f"Received: {message.decode('utf-8')}")

    # Close the client socket
    client_socket.close()
    print(f"Connection to {addr} closed")
    print(clientInfo)

# Create a socket object
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind the server to a specific address and port
host = '127.0.0.1'  # Server's IP address
port = 12345       # Port to listen on
server_socket.bind((host, port))

# Listen for incoming connections
server_socket.listen(5)

print(f"Server listening on {host}:{port}")

# Accept client connections
while True:
    client_socket, addr = server_socket.accept()
    thread = threading.Thread(target = client_thread, args = (client_socket, addr, ))
    thread.start()
    
    
