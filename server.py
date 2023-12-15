import socket
import threading
import sys
import os
import logging
import math
#configure logging file
logging.basicConfig(filename='server.log', filemode='w', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

downloads_directory = "./downloads"

def send_file(clientName, client_socket, filename):
    file_path = f"{downloads_directory}/{filename}"
    file_size = os.path.getsize(file_path)
    total_packets = math.ceil(file_size / 1024)
    try:
        client_socket.send(f"{total_packets}".encode("utf-8"))
        with open(file_path, 'rb') as file:

            for x in range(total_packets):
                file_data = file.read(1024)
                client_socket.send(file_data)
                ack = client_socket.recv(1024)

            logging.info(f"Sent file '{filename}' to {clientName}")
    except FileNotFoundError:
        logging.error(f"File '{filename}' not found on the server")

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
    host = "127.0.0.1"
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
    for clientName, client_data in clientInfo.items():
        if exclude is None or clientName not in exclude:
            client_data["socket"].send(message.encode("utf-8"))

def Unicast(message, clientInfo, recipient):
    clientInfo[recipient]["socket"].send(message.encode("utf-8"))

def client_thread(client_socket, addr, clientInfo, names):
    global downloads_directory
    print(f"Connection from {addr[0]}: {addr[1]}")
    
    clientName = client_socket.recv(1024).decode("utf-8").strip()

    if clientName in names:
        client_socket.send("Client already exists with that name".encode("utf-8"))
        logging.warning(f"refused connection from {addr[0]}: {addr[1]} - name {clientName} already exists")

        client_socket.close()
    else:
        logging.info(f"accepted connection from {clientName} at {addr[0]}: {addr[1]}")
        client_socket.send(f"Welcome to the Server {clientName}".encode("utf-8"))
        names.append(clientName)
        clientInfo[clientName] = {
            "address" : addr,
            "socket" : client_socket
        }

        broadcast(f"{clientName} has joined", clientInfo, exclude=[clientName])

        logging.info(f"join message for {clientName} broadcast")

        while True:
            try:
                message = client_socket.recv(1024).decode("utf-8")
                if not message:
                    break
                elif message.lower() == "clients":
                    client_socket.send(str(names).encode("utf-8"))
                    logging.info(f"sent connected client list to {clientName}")
                elif message.lower() == "downlist":
                    client_socket.send(str(os.listdir(downloads_directory)).encode("utf-8"))
                    logging.info(f"sent downloadables list to {clientName}")
                elif message.lower() == "help":
                    continue
                elif " " in message:
                    brick = message.lower().split(" ")
                    if brick[0] == "uni":
                        recipient = brick[1]
                        if (recipient in names) and (recipient != clientName):

                            logging.info(f"Unicast started from {clientName} to {recipient}")
                            client_socket.send(f"UniCasting to {recipient}".encode("utf-8"))
                            while True:
                                incoming_message = client_socket.recv(1024).decode("utf-8")
                                if incoming_message.lower() == "exit":
                                    client_socket.send(f"Leaving UniCast with {recipient}".encode("utf-8"))
                                    logging.info(f"{clientName} exits unicast with {recipient}")
                                    break
                                else:
                                    uni_message = f"{clientName} whispers: {incoming_message}"
                                    Unicast(uni_message, clientInfo, recipient)
                                    logging.info(f"{clientName} unicasts '{incoming_message}' to {recipient}")


                        else:
                            client_socket.send(f"{recipient} is not a valid client".encode("utf-8"))
                            logging.warning(f"{clientName} attempts invalid unicast to {recipient}")
                            continue

                    elif brick[0] == "down":
                        client_socket.send(f"FILE_DOWNLOAD_HEADER {brick[1]} {brick[2]}".encode("utf-8"))
                        ack = client_socket.recv(1024)
                        send_file(clientName, client_socket, brick[1])
                    else:
                        broadcast(f"{clientName}: {message}", clientInfo, exclude=[clientName])
                        logging.info(f"{clientName} broadcasts '{message}'")
                else:
                    broadcast(f"{clientName}: {message}", clientInfo, exclude=[clientName])
                    logging.info(f"{clientName} broadcasts '{message}'")
            except socket.error as e:
                print(f"Error receiving data: {e}")
                logging.error(f"error receiving data from {clientName} - server closed connection")
                break
        
        logging.info(f"{clientName} disconnected from server")
        #delete client from dictionary and allowed names and broadcast leaving message
        del clientInfo[clientName]
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
            logging.error(f"Error accepting connection - {e}")


server_runtime()