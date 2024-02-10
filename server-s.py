import socket
import signal
import sys
import threading
import time

# Define a global flag to control server loop execution
not_stopped = True
connection_count = 0
connection_lock = threading.Lock()

def signal_handler(signum, frame):
    global not_stopped
    not_stopped = False
    print("Signal received, shutting down the server...")

def handle_client(client_socket):
    global connection_count
    try:
        client_socket.sendall(b'accio\r\n')
        client_socket.settimeout(10)  # Set timeout for receiving data

        total_bytes_received = 0
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            total_bytes_received += len(data)

        # Ensure only the number of bytes received is printed
        print(f"{total_bytes_received}")

    except socket.timeout:
        sys.stderr.write("ERROR: Connection timed out\n")
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
    finally:
        with connection_lock:
            connection_count -= 1
        client_socket.close()

def main():
    global not_stopped
    global connection_count

    if len(sys.argv) != 2:
        print("ERROR: Invalid number of arguments", file=sys.stderr)
        return  # Return instead of exit to avoid using sys.exit()

    port = int(sys.argv[1])
    if not (0 <= port <= 65535):
        print("ERROR: Port must be within range 0-65535", file=sys.stderr)
        return

    # Register signal handlers
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server_socket.bind(('0.0.0.0', port))
            server_socket.listen(10)
            print(f"Server listening on port {port}")

            while not_stopped:
                try:
                    server_socket.settimeout(1)
                    client_socket, _ = server_socket.accept()
                    with connection_lock:
                        if connection_count < 10:
                            connection_count += 1
                            threading.Thread(target=handle_client, args=(client_socket,)).start()
                        else:
                            print("ERROR: Maximum connection limit reached", file=sys.stderr)
                            client_socket.close()
                except socket.timeout:
                    continue
                except Exception as e:
                    print(f"ERROR: {str(e)}", file=sys.stderr)

            # Wait for active connections to finish
            while connection_count > 0:
                time.sleep(1)
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)

    print("Server shutdown completed.")

if __name__ == "__main__":
    main()
