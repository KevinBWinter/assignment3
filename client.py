import sys
import socket

def send_file_contents(s, filename):
    try:
        with open(filename, 'rb') as file:
            while True:
                chunk = file.read(10000)
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
            
            expected_commands = [b'accio\r\n', b'accio\r\n']
            confirmations = [b'confirm-accio\r\n', b'confirm-accio-again\r\n\r\n']

            for command, confirmation in zip(expected_commands, confirmations):
                buffer = b""
                while not buffer.endswith(command):
                    data = s.recv(1024)
                    if not data:
                        raise Exception("Connection closed by server")
                    buffer += data
                s.sendall(confirmation)
            
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
    except ValueError:
        sys.stderr.write("ERROR: Port must be an integer\n")
        sys.exit(1)

    if not (1 <= port <= 65535):
        sys.stderr.write("ERROR: Port number out of valid range\n")
        sys.exit(1)

    main(host, port, filename)
