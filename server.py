import sys
import socket
import signal
import threading
import os

def signal_handler(sig, frame):
    print("Signal received, shutting down server.")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)

if len(sys.argv) != 3:
    sys.stderr.write("ERROR: Usage: python3 server.py <PORT> <FILE-DIR>\n")
    sys.exit(1)

try:
    port = int(sys.argv[1])
    if port < 1 or port > 65535:
        raise ValueError
except ValueError:
    sys.stderr.write("ERROR: Invalid port number\n")
    sys.exit(1)

file_dir = sys.argv[2]
if not os.path.exists(file_dir):
    os.makedirs(file_dir)

try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen()
    print(f"Server listening on port {port}")
except Exception as e:
    sys.stderr.write(f"ERROR: {str(e)}\n")
    sys.exit(1)

def handle_client(client_socket, connection_id):
    try:
        print(f"Connection {connection_id} established from {client_socket.getpeername()}")
        client_socket.sendall(b'accio\r\n')
        client_socket.settimeout(10)
        data = b''
        while True:
            chunk = client_socket.recv(1024)
            if not chunk:
                break
            data += chunk
        file_path = os.path.join(file_dir, f"{connection_id}.file")
        with open(file_path, 'wb') as file:
            file.write(data)
        print(f"Data saved to {file_path}")
    except socket.timeout:
        file_path = os.path.join(file_dir, f"{connection_id}.file")
        with open(file_path, 'wb') as file:
            file.write(b'ERROR')
        print(f"Timeout occurred, wrote ERROR to {file_path}")
    finally:
        client_socket.close()
        print(f"Connection {connection_id} closed")

connection_counter = 0
try:
    while True:
        client_socket, addr = server_socket.accept()
        connection_counter += 1
        threading.Thread(target=handle_client, args=(client_socket, connection_counter)).start()
except KeyboardInterrupt:
    server_socket.close()
    print("Server shut down")
