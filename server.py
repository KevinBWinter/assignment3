import sys
import socket
import signal
import threading
import os

def signal_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)

if len(sys.argv) != 3:
    sys.stderr.write("ERROR: Incorrect number of arguments\n")
    sys.exit(1)

try:
    port = int(sys.argv[1])
    if port < 0 or port > 65535:
        raise ValueError
except ValueError:
    sys.stderr.write("ERROR: Invalid port number\n")
    sys.exit(1)

file_dir = sys.argv[2]
if not os.path.exists(file_dir):
    os.makedirs(file_dir)

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', port))
server_socket.listen()

def handle_client(client_socket, connection_id):
    try:
        client_socket.sendall(b'accio\r\n')
        client_socket.settimeout(10)
        data = b''
        while True:
            chunk = client_socket.recv(1024)
            if not chunk:
                break
            data += chunk
        with open(f'{file_dir}/{connection_id}.file', 'wb') as file:
            file.write(data)
    except socket.timeout:
        with open(f'{file_dir}/{connection_id}.file', 'wb') as file:
            file.write(b'ERROR')
    finally:
        client_socket.close()

connection_counter = 0
try:
    while True:
        client_socket, _ = server_socket.accept()
        connection_counter += 1
        threading.Thread(target=handle_client, args=(client_socket, connection_counter)).start()
except KeyboardInterrupt:
    server_socket.close()
