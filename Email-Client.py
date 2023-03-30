import socket
import urllib.request


# Set up client constants
SMTP_PORT = 25
POP3_PORT = 110
HOST = '15.204.245.120' #'localhost'
USERNAME = 'client_username'
PASSWORD = 'client_password'


def get_public_ip_address():
    try:
        with urllib.request.urlopen("http://icanhazip.com") as response:
            public_ip = response.read().decode("utf-8").strip()
    except Exception as e:
        public_ip = "127.0.0.1"
    return public_ip


def get_public_ipv4():
    try:
        with urllib.request.urlopen("https://api.ipify.org") as response:
            public_ipv4 = response.read().decode("utf-8")
    except Exception as e:
        public_ipv4 = get_public_ip_address()
    return public_ipv4


CLIENT_IP = get_public_ipv4()


# Define SMTP functions
def smtp_client():
    # Connect to SMTP server socket
    smtp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    smtp_client_socket.connect((HOST, SMTP_PORT))

    # Receive SMTP greeting from server
    data = smtp_client_socket.recv(1024)
    print(data.decode())

    # Send EHLO command to start SMTP handshake
    # smtp_client_socket.send(b'EHLO localhost\r\n')
    smtp_client_socket.send('EHLO {}\r\n'.format(CLIENT_IP).encode())

    # Receive response from server
    data = smtp_client_socket.recv(1024)
    print(data.decode())

    # Close SMTP connection
    smtp_client_socket.close()
    print("smtp closed")


# Define POP3 functions
def pop3_client():
    # Connect to POP3 server socket
    pop3_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pop3_client_socket.connect((HOST, POP3_PORT))

    # Receive POP3 greeting from server
    data = pop3_client_socket.recv(1024)
    print(data.decode(), end='')

    # Send USER command to start POP3 handshake
    pop3_client_socket.send('USER {}\r\n'.format(USERNAME).encode())
    data = pop3_client_socket.recv(1024)
    print(data.decode(), end='')

    # Send PASS command to continue POP3 handshake
    pop3_client_socket.send('PASS {}\r\n'.format(PASSWORD).encode())
    data = pop3_client_socket.recv(1024)
    print(data.decode(), end='')

    # send LIST command to list messages
    pop3_client_socket.send(b"LIST\r\n")
    data = pop3_client_socket.recv(1024)
    print(data.decode())

    # send QUIT command to log out and close the connection
    pop3_client_socket.send(b"QUIT\r\n")
    data = pop3_client_socket.recv(1024)
    print(data.decode())

    # Close POP3 connection
    pop3_client_socket.close()
    print('client closed')


# Start SMTP and POP3 clients
smtp_client() # Currently only connection code.
pop3_client() # Currently only connection code.


# Run Loop
    # create connection ^ ^, send email
    # ||
    # create connection ^ ^, check email
# Close connection

