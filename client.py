import select
import socket
import ipaddress
import threading
import sys
import os
import time

global_stop = threading.Event()

def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def print_loading(loading_image):
    hide_cursor()

    anims = ["L", "Lo", "Loa", "Load", "Loadi", "Loadin", "Loading"]
    pos = 0
    while loading_image.is_set():
        print("\r" + " " * 7 + "\r", end="", flush=True)
        print(anims[pos], end="", flush=True)
        pos += 1
        pos = pos % 7
        time.sleep(0.1)
    print("\r" + " " * 7 + "\r", end="", flush=True)

    show_cursor()

def server_listen(client_socket):
    while not global_stop.is_set():
        try:
            incoming, _, _ = select.select([client_socket], [], [], 0)

            if incoming:
                data = client_socket.recv(1024).decode('utf-8').strip()
                if not data:
                    #if data is empty, the server closed the connection
                    global_stop.set()
                    break
                elif "FILE_DOWNLOAD_HEADER" in data:
                    parts = data.strip().split(" ")
                    receive_file(client_socket, parts[1], parts[2])
                elif data[0] == '[':
                    box(string_to_array(data))
                else:
                    print(data)

            else:
                continue
        except ConnectionAbortedError:
            break

def receive_file(client_socket, filename, save_directory):
    loading_image = threading.Event()
    loading_image.set()
    load_thread = threading.Thread(target=print_loading, args=(loading_image,))
    load_thread.start()
    
    try:
        client_socket.send(b'ACK')
        total_packets = int(client_socket.recv(1024).decode("utf-8"))
        os.makedirs(save_directory, exist_ok=True)
        with open(f"{save_directory}/{filename}", 'wb') as file:
            for x in range(total_packets):
                file_data = client_socket.recv(1024)
                file.write(file_data)
                client_socket.send(b'ACK')  # Send acknowledgment back to server
        loading_image.clear()
        load_thread.join()
        
        print(f"File '{filename}' received and saved to {save_directory}")
    except Exception as e:
        print(f"Error receiving file: {e}")

def box(lines):
    longest = len(max(lines, key=len))
    print("".join([chr(0x2554)] + [chr(0x2550) for _ in range(longest+2)] + [chr(0x2557)]))
    for x in range(len(lines)):
        print(chr(0x2551) + " " + lines[x].ljust(longest) + " " +chr(0x2551))
    print("".join([chr(0x255A)] + [chr(0x2550) for _ in range(longest+2)] + [chr(0x255D)]))

def help_box():
    box(["clients = see all other connected clients", "", "uni [name] = begin a 1-1 messenger with user [name]", "", "downlist = list all downloadable files from server", "", "down [file] [location] = download file [file] into folder [location]", "", "exit = disconnect from server and close program", "", "all other messages will be broadcast to all other clients connected",])

def string_to_array(string):
    string = string[1:-1]
    string_arr = string.split(",")
    for x in range(len(string_arr)):
        string_arr[x] = string_arr[x].strip()[1:-1]
    
    return string_arr

if len(sys.argv) != 4:
    print("Invalid number of arguments")
    exit()
else:
    try:
        ipaddress.ip_address(sys.argv[2])
    except ValueError:
        print("Invalid hostname")
        exit()

    try:
        int(sys.argv[3])
    except ValueError:
        print("Non-int Port number")
        exit()
    
    if int(sys.argv[3]) < 0 or int(sys.argv[3]) > 65535:
        print("Invalid port number")
        exit()

#set name, hostname, and port from validated arguments
name = sys.argv[1]
hostname = sys.argv[2]
port = int(sys.argv[3])

#create socket object skeleton
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#connect to the server with hostname and port
client_socket.connect((hostname, port))

client_socket.send(name.encode('utf-8'))

#check if name is allowed
confirmation = client_socket.recv(1024).decode('utf-8').strip()
print(confirmation)
if confirmation == "Client already exists with that name":
    client_socket.close()
    exit()

#begin listening to messages from server
listen_thread = threading.Thread(target=server_listen, args=(client_socket,))
listen_thread.start()

#start messaging
while True:
    try:
        message = input()
        if message.lower() == 'help':
            help_box()
        elif " " in message:
            parts = message.lower().split(" ")
            if parts[0] == "uni":
                client_socket.send(message.encode('utf-8'))
                while True:
                    message = input()
                    client_socket.send(message.encode('utf-8'))
                    if message.lower() == "exit":
                        break
            elif parts[0] == "down":
                client_socket.send(message.encode('utf-8'))
        elif message.lower() == "exit":
            break
        else:
            client_socket.send(message.encode('utf-8'))
    except EOFError:
        # Handle Ctrl+D (EOF) to exit gracefully
        print("\nExiting...")
        break

global_stop.set()
listen_thread.join()
# Close the client socket
client_socket.close()