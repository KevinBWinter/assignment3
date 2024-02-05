import sys
import socket

def send_file_contents(s, filename):
    with open(filename, 'rb') as file:
        while True:
            chunk = file.read(10000)
            if not chunk:
                break
            s.sendall(chunk)

def main(hostname, port, filename):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((hostname, port))
            # Wait for the server to send "accio\r\n"
            data = s.recv(1024)
            if data != b'accio\r\n':
                raise Exception("First accio command not received")
            s.sendall(b'confirm-accio\r\n')

            # Wait for the second "accio\r\n"
            data = s.recv(1024)
            if data != b'accio\r\n':
                raise Exception("Second accio command not received")
            s.sendall(b'confirm-accio-again\r\n\r\n')

            # Send file contents
            send_file_contents(s, filename)

    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.stderr.write("ERROR: Usage: python3 client.py <HOSTNAME-OR-IP> <PORT> <FILENAME>\n")
        sys.exit(1)

    _, host, port_str, filename = sys.argv
    try:
        port = int(port_str)
        if port < 1 or port > 65535:
            raise ValueError("Port number out of valid range")
    except ValueError as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        sys.exit(1)

    main(host, port, filename)
