import socket
import signal
import sys
import threading
import time

not_stopped = True
connection_count = 0
connection_lock = threading.Lock()
received_bytes = 0

def signal_handler(signum, frame):
    global not_stopped
    not_stopped = False

def handle_client(client_socket):
    global connection_count, received_bytes
    try:
        client_socket.sendall(b'accio\r\n')
        client_socket.settimeout(10)
        
        confirmation = client_socket.recv(1024)
        if confirmation.strip() != b'confirm-accio':
            return

        client_socket.sendall(b'accio\r\n')

        second_confirmation = client_socket.recv(1024)
        if second_confirmation.strip() != b'confirm-accio-again':
            return

        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            with connection_lock:
                received_bytes += len(data)

    except socket.timeout:
        pass
    except Exception as e:
        pass
    finally:
        with connection_lock:
            connection_count -= 1
        client_socket.close()

def main():
    global not_stopped, connection_count, received_bytes

    if len(sys.argv) != 2:
        sys.exit(1)

    port = int(sys.argv[1])
    if port < 0 or port > 65535:
        sys.exit(1)

    signal.signal(signal.SIGQUIT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('0.0.0.0', port))
        server_socket.listen(10)

        while not_stopped:
            try:
                server_socket.settimeout(1)
                client_socket, _ = server_socket.accept()
                with connection_lock:
                    if connection_count < 10:
                        connection_count += 1
                        threading.Thread(target=handle_client, args=(client_socket,)).start()
                    else:
                        client_socket.close()
            except socket.timeout:
                continue
            except Exception as e:
                pass

        while connection_count > 0:
            time.sleep(1)

    print(f"Received {received_bytes} bytes")

if __name__ == "__main__":
    main()
