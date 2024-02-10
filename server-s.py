import socket
import signal
import sys
import time

# Define a global flag to control server loop execution
not_stopped = True

def signal_handler(signum, frame):
    global not_stopped
    not_stopped = False
    print("Signal received, shutting down the server...")

def handle_client(client_socket):
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
        client_socket.close()

def main():
    global not_stopped

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
        server_socket.listen(10)  # Allow up to 10 pending connections

        print(f"Server listening on port {port}")

        while not_stopped:
            try:
                client_socket, client_address = server_socket.accept()
                print(f"Accepted connection from {client_address}")
                handle_client(client_socket)
            except socket.timeout:
                continue  # Go back to checking the not_stopped flag
            except OSError as e:
                if not_stopped:  # If the server is stopping, don't print the error message
                    sys.stderr.write(f"ERROR: {str(e)}\n")

    finally:
        server_socket.close()

if __name__ == "__main__":
    main()
