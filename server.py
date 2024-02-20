import sys
import socket
import threading
import os
import signal

# Flag to indicate whether the server should continue running
running = True

# Lock for synchronizing access to the connection counter
counter_lock = threading.Lock()

# Handle SIGINT, SIGTERM, SIGQUIT signals
def signal_handler(sig, frame):
    global running
    running = False
    server_socket.close()  # Close the server socket to break out of the accept loop

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
    server_socket.setblocking(False)  # Set the socket to non-blocking mode
except Exception as e:
    sys.stderr.write(f"ERROR: {str(e)}\n")
    sys.exit(1)

# Function to handle each client connection
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
        file_path = os.path.join(file_dir, f"{connection_id}.file")
        with open(file_path, 'wb') as file:
            file.write(data)
    except socket.timeout:
        file_path = os.path.join(file_dir, f"{connection_id}.file")
        with open(file_path, 'wb') as file:
            file.write(b'ERROR')
    finally:
        client_socket.close()

# Main loop to accept and handle client connections
connection_counter = 0
try:
    while running:
        try:
            client_socket, _ = server_socket.accept()
            with counter_lock:
                connection_counter += 1
                threading.Thread(target=handle_client, args=(client_socket, connection_counter)).start()
        except BlockingIOError:
            # This exception is expected when the server socket is in non-blocking mode and no connections are pending
            continue
except KeyboardInterrupt:
    pass  # Ignore KeyboardInterrupt as we're already handling it with the signal handler

# Wait for all threads to finish
for thread in threading.enumerate():
    if thread != threading.main_thread():
        thread.join()
