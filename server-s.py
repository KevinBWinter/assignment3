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
    # Your existing code for handle_client remains unchanged.

def main():
    global not_stopped
    global connection_count

    if len(sys.argv) != 2:
        sys.stderr.write("ERROR: Invalid number of arguments\n")
        sys.exit(1)

    port = int(sys.argv[1])
    if not (0 <= port <= 65535):
        sys.stderr.write("ERROR: Port must be within range 0-65535\n")
        sys.exit(1)

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
                            sys.stderr.write("ERROR: Maximum connection limit reached\n")
                            client_socket.close()
                except socket.timeout:
                    continue
                except Exception as e:
                    sys.stderr.write(f"ERROR: {str(e)}\n")

            while connection_count > 0:
                time.sleep(1)
    except OverflowError:
        sys.stderr.write("ERROR: Port must be within range 0-65535\n")
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")

if __name__ == "__main__":
    main()
