import socket
import threading
import sys


def serverStart():
    if len(sys.argv) != 2:
        print("invalid number of arguments")
        exit()
    else:
        try:
            int(sys.argv[1])
        except ValueError:
            print("Non-int Port number")
            exit()
        
        if int(sys.argv[1]) < 0 or int(sys.argv[1]) > 65535:
            print("Invalid port number")
            exit()

    #intialise connections dictionary and port
    host = '127.0.0.1'
    port = int(sys.argv[1])

    #create socket object skeleton
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    #bind the server to default address with specified port
    server_socket.bind((host, port))

    #listen for incoming connections
    server_socket.listen(5)

    print(f"Server listening on {host}:{port}")

    return server_socket

def broadcast(message, clientInfo, exclude=None):
    #send message to each client
    for client_addr, client_data in clientInfo.items():
        if exclude is None or client_addr not in exclude:
            client_data["socket"].send(message.encode('utf-8'))

def Unicast(message, clientInfo, recipient):
    clientInfo[recipient].send(message.encode('utf-8'))

def client_thread(client_socket, addr, clientInfo, names):
    print(f"Connection from {addr[0]}: {addr[1]}")
    
    clientName = client_socket.recv(1024).decode('utf-8').strip()

    if clientName in names:
        client_socket.send("Client already exists with that name".encode('utf-8'))
        client_socket.close()
    else:
        client_socket.send(f"Welcome to the Server {clientName}".encode('utf-8'))
        names.append(clientName)
        clientInfo[addr] = {
            "name" : clientName,
            "socket" : client_socket
        }

        broadcast(f"{clientName} has joined", clientInfo, exclude=[addr])

        while True:
            try:
                message = client_socket.recv(1024)
                if not message:
                    break
                elif message == "clients":
                    client_socket.send(f"Welcome to the Server {clientName}".encode('utf-8'))
                elif message == "downlist":
                    client_socket.send(f"Welcome to the Server {clientName}".encode('utf-8'))
                elif message.split(" ")[0] == "uni":
                    print("s")
                elif message.split(" ")[0] == "down":
                    print("s")
                else:
                    broadcast(f"{clientName}: {message}", clientInfo,)
            except socket.error as e:
                print(f"Error receiving data: {e}")
                break

        #delete client from dictionary and allowed names and broadcast leaving message
        del clientInfo[addr]
        broadcast(f"{clientName} has left", clientInfo)
        names.remove(clientName)

        #close the client socket
        client_socket.close()

def server_runtime():
    clientInfo = {}
    names = []

    server_socket = serverStart()

    #accept client connections
    while True:
        try:
            client_socket, addr = server_socket.accept()
            thread = threading.Thread(target=client_thread, args=(client_socket, addr, clientInfo, names))
            thread.start()
        except socket.error as e:
            print(f"Error accepting connection: {e}")


server_runtime()