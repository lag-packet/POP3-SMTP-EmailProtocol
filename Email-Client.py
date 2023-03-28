import socket

# Set up client constants
SMTP_PORT = 25
POP3_PORT = 110
HOST = '15.204.245.120'


# Define SMTP functions
def smtp_client():
    # Connect to SMTP server socket
    smtp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    smtp_client_socket.connect((HOST, SMTP_PORT))

    # Receive SMTP greeting from server
    data = smtp_client_socket.recv(1024)
    print(data.decode())

    # Send EHLO command to start SMTP handshake
    smtp_client_socket.send(b'EHLO localhost\r\n')

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
    pop3_client_socket.send(b'USER username\r\n')
    data = pop3_client_socket.recv(1024)
    print(data.decode(), end='')

    # Send PASS command to continue POP3 handshake
    pop3_client_socket.send(b'PASS password\r\n')
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

