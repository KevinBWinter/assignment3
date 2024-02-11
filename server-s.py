import socket
import signal
import sys
import threading

# Define global control variables
not_stopped = True
connection_count = 0
connection_lock = threading.Lock()

def signal_handler(signum, frame):
    global not_stopped
    not_stopped = False
    print("Shutting down server...")

def handle_client(client_socket):
    global connection_count
    try:
        client_socket.sendall(b'accio\r\n')  # Initial command
        client_socket.settimeout(10)  # Timeout for client response

        # Wait for and verify confirmations here if your protocol requires it

        total_bytes_received = 0
        while True:
            data = client_socket.recv(4096)
            if not data:
                break  # Connection closed
            total_bytes_received += len(data)

        # Assuming the test expects a specific output format
        print(f"{total_bytes_received} bytes received")

    except socket.timeout:
        sys.stderr.write("ERROR: Connection timed out\n")
    finally:
        with connection_lock:
            connection_count -= 1
        client_socket.close()

def main():
    global not_stopped

    if len(sys.argv) != 2:
        sys.stderr.write("ERROR: Invalid number of arguments\n")
        return

    port = int(sys.argv[1])
    if not (0 <= port <= 65535):
        sys.stderr.write("ERROR: Port must be within range 0-65535\n")
        return

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen(10)
        print(f"Server listening on port {port}")

        while not_stopped:
            try:
                server_socket.settimeout(1)
                client_socket, addr = server_socket.accept()
                print(f"Connection accepted from {addr}")
                with connection_lock:
                    if connection_count < 10:
                        connection_count += 1
                        threading.Thread(target=handle_client, args=(client_socket,)).start()
                    else:
                        sys.stderr.write("ERROR: Max connection limit reached\n")
                        client_socket.close()
            except socket.timeout:
                continue  # Normal timeout, just check for stop condition
    except Exception as e:
        sys.stderr.write(f"ERROR: Unexpected error {e}\n")
    finally:
        server_socket.close()
        print("Server shutdown.")

if __name__ == "__main__":
    main()
