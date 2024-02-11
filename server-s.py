import socket
import signal
import sys
import threading

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
        # Send the initial accio command to the client
        client_socket.sendall(b'accio\r\n')
        client_socket.settimeout(10)  # Set timeout for receiving data
        
        # Wait for confirmation
        confirmation = client_socket.recv(1024)
        if confirmation.strip() != b'confirm-accio':
            raise Exception("Incorrect confirmation received")

        # Send the accio command again
        client_socket.sendall(b'accio\r\n')

        # Wait for the second confirmation
        second_confirmation = client_socket.recv(1024)
        if second_confirmation.strip() != b'confirm-accio-again':
            raise Exception("Incorrect second confirmation received")

        total_bytes_received = 0
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            total_bytes_received += len(data)

        print(f"Received {total_bytes_received} bytes")

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
        sys.stderr.write("ERROR: Invalid number of arguments\n")
        sys.exit(1)

    port = int(sys.argv[1])

    # Register signal handlers
    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

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

if __name__ == "__main__":
    main()
