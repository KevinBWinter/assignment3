import sys
import socket

def main(hostname, port, filename):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((hostname, int(port)))
            print("Connection established")
    except Exception as e:
        sys.stderr.write(f"ERROR: {str(e)}\n")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python3 client.py <HOSTNAME-OR-IP> <PORT> <FILENAME>")
        sys.exit(1)

    _, host, port, filename = sys.argv
    main(host, port, filename)
