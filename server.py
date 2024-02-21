
import sys
import socket
import threading
import os
import signal

# Handle SIGINT, SIGTERM, SIGQUIT signals
def signal_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGQUIT, signal_handler)

# Validate command-line arguments
if len(sys.argv) != 3:
    sys.stderr.write("ERROR: Usage: python3 server.py <PORT> <FILE-DIR>\n")
    sys.exit(1)

# Validate port number
try:
    port = int(sys.argv[1])
    if port < 1 or port > 65535:
        raise ValueError
except ValueError:
    sys.stderr.write("ERROR: Invalid port number\n")
    sys.exit(1)

# Create directory for storing files
file_dir = sys.argv[2]
if not os.path.exists(file_dir):
    os.makedirs(file_dir)

# Create server socket
try:
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', port))
    server_socket.listen()
except Exception as e:
    sys.stderr.write(f"ERROR: {str(e)}\n")
    sys.exit(1)

# Function to handle each client connection
def handle_client(client_socket, connection_id):
    try:
        # Send the 'accio' command twice as expected by the client
        client_socket.sendall(b'accio\r\n')
        client_socket.sendall(b'accio\r\n')

        client_socket.settimeout(10)
        data = b''
        while True:
            chunk = client_socket.recv(1024)
            if not chunk:
                break
            data += chunk

        if data:  # Check if any data was received
            file_path = os.path.join(file_dir, f"{connection_id}.file")
            with open(file_path, 'wb') as file:
                file.write(data)
        else:  # No data received, create an empty file
            file_path = os.path.join(file_dir, f"{connection_id}.file")
            open(file_path, 'wb').close()

    except socket.timeout:
        file_path = os.path.join(file_dir, f"{connection_id}.file")
        with open(file_path, 'wb') as file:
            file.write(b'ERROR')
    finally:
        client_socket.close()

# Main loop to accept and handle client connections
connection_counter = 0
try:
    while True:
        client_socket, _ = server_socket.accept()
        connection_counter += 1
        threading.Thread(target=handle_client, args=(client_socket, connection_counter)).start()
except KeyboardInterrupt:
    server_socket.close()
