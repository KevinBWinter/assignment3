import sys
import socket

def send_file_contents(s, filename):
    try:
        with open(filename, 'rb') as file:
            while True:
                chunk = file.read(1024)  # Use a smaller chunk size for better compatibility
                if not chunk:
                    break
                s.sendall(chunk)
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        sys.exit(1)

def main(hostname, port, filename):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            s.connect((hostname, port))
            s.sendall(b'accio\r\n')  # Send the accio command

            buffer = b""
            while not buffer.endswith(b'accio\r\n'):  # Wait for the accio command confirmation
                data = s.recv(1024)
                if not data:
                    raise Exception("Connection closed by server")
                buffer += data
            
            send_file_contents(s, filename)  # Send the file contents

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
    except ValueError:
        sys.stderr.write("ERROR: Port must be an integer\n")
        sys.exit(1)

    if not (1 <= port <= 65535):
        sys.stderr.write("ERROR: Port number out of valid range\n")
        sys.exit(1)

    main(host, port, filename)

