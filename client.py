import select
import socket
import ipaddress
import threading
import shutil
import sys

global_stop = threading.Event()

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

                characters, _ = shutil.get_terminal_size()
                print('\r' + ' ' * characters + '\r' + data + "\n")
                print("Enter a message or command ('help' for commands): ", end='', flush=True)
            else:
                continue
        except ConnectionAbortedError:
            break

def box(lines):
    longest = len(max(lines, key=len))
    print("".join([chr(0x2554)] + [chr(0x2550) for _ in range(longest+2)] + [chr(0x2557)]))
    for x in range(len(lines)):
        print(chr(0x2551) + " " + lines[x].ljust(longest) + " " +chr(0x2551))
    print("".join([chr(0x255A)] + [chr(0x2550) for _ in range(longest+2)] + [chr(0x255D)]))

def help_box():
    box(["clients = see all other connected clients", "", "uni [name] = begin a 1-1 messenger with user [name]", "", "downlist = list all downloadable files from server", "", "down [file] [location] = download file [file] into folder [location]", "", "exit = disconnect from server and close program", "", "all other messages will be broadcast to all other clients connected",])

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
        message = input("Enter a message or command ('help' for commands): ")
        if message.lower() == 'help':
            help_box()
        elif message.lower() == "exit":
            break
        client_socket.send(message.encode('utf-8'))
    except EOFError:
        # Handle Ctrl+D (EOF) to exit gracefully
        print("\nExiting...")
        break

global_stop.set()
listen_thread.join()
# Close the client socket
client_socket.close()