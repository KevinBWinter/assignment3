import sys
import socket

def main(hostname, port, filename):
    try:
        # Attempt to establish a TCP connection with the specified timeout
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)  # Set timeout for connecting and operations to 10 seconds
            s.connect((hostname, int(port)))
            # Placeholder for sending and receiving logic
            print("Connection established")
            # After connection logic here, ensure to close the connection gracefully

    except socket.timeout:
        sys.stderr.write("ERROR: Connection timed out\n")
        sys.exit(1)
    except socket.gaierror:
        sys.stderr.write("ERROR: Address-related error connecting to server\n")
        sys.exit(1)
    except socket.error as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        sys.exit(1)
    except ValueError:
        # This catches scenarios where port is not an integer
        sys.stderr.write("ERROR: Port must be an integer\n")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.stderr.write("Usage: python3 client.py <HOSTNAME-OR-IP> <PORT> <FILENAME>\n")
        sys.exit(1)

    _, host, port, filename = sys.argv
    
    # Additional basic validation could be included here for port number
    try:
        port = int(port)
        if port < 1 or port > 65535:
            raise ValueError("Port number is out of valid range")
    except ValueError as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        sys.exit(1)

    main(host, port, filename)
