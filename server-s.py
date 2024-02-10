import socket
import signal
import sys
import time
import threading

# Define global variables
not_stopped = True
connection_count = 0
connection_lock = threading.Lock()

# Signal handler function
def signal_handler(signum, frame):
    global not_stopped
    not_stopped = False
    print("Signal received, shutting down the server...")

# Function to handle client connections
def handle_client(client_socket):
    global connection_count
    try:
        client_socket.send(b"accio\r\n")  # Sending initial data to the client
        client_socket.settimeout(10)  # Set timeout for receiving data

        total_bytes_received = 0
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            total_bytes_received += len(data)

        if total_bytes_received == 0:
            sys.stderr.write("ERROR: No data received\n")
        else:
            print(f"Received {total_bytes_received} bytes")

    except socket.timeout:
        sys.stderr.write("ERROR: Connection timed out\n")
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
    finally:
        with connection_lock:
            connection_count -= 1
        client_socket.close()

# Main function
def main():
    global not_stopped
    global connection_count

    if len(sys.argv) != 2:
        sys.stderr.write("ERROR: Invalid number of arguments\n")
        sys.exit(1)

    port = int(sys.argv[1])

    # Register signal handlers
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Allow reusing the address

    try:
        if not (0 <= port <= 65535):
            sys.stderr.write("ERROR: Port must be within range 0-65535\n")
            sys.exit(1)

        server_socket.bind(('0.0.0.0', port))
        server_socket.listen(10)

        print(f"Server listening on port {port}")

        while not_stopped:
            try:
                server_socket.settimeout(1)  # Non-blocking accept with a timeout to check not_stopped flag
                client_socket, client_address = server_socket.accept()
                with connection_lock:
                    connection_count += 1
                print(f"Accepted connection from {client_address}")
                client_thread = threading.Thread(target=handle_client, args=(client_socket,))
                client_thread.start()
            except socket.timeout:
                continue  # Go back to checking the not_stopped flag
            except OSError as e:
                if not_stopped:  # If the server is stopping, don't print the error message
                    sys.stderr.write(f"ERROR: {str(e)}\n")

        while connection_count > 0:
            time.sleep(1)  # Wait for active connections to finish

    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
