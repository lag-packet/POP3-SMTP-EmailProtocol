import socket
import threading

# Set up server constants
SMTP_PORT = 25
POP3_PORT = 110
HOST = 'localhost'


# Define SMTP functions
def smtp_server():
    # Create SMTP server socket
    smtp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    smtp_server_socket.bind((HOST, SMTP_PORT))
    smtp_server_socket.listen(1)

    print('SMTP server listening on {}:{}'.format(HOST, SMTP_PORT))

    while True:
        # Accept incoming SMTP connection
        client_socket, address = smtp_server_socket.accept()
        print('SMTP client connected from {}'.format(address))

        # Send initial SMTP greeting
        client_socket.send(b'220 localhost ESMTP server ready\r\n')

        # Start SMTP handshake
        data = client_socket.recv(1024)
        if data.startswith(b'EHLO'):
            client_socket.send('250-localhost greets {}\r\n'.format(data.split()[1]).encode())
            client_socket.send(b'250-PIPELINING\r\n')
            client_socket.send(b'250-ENHANCEDSTATUSCODES\r\n')
            client_socket.send(b'250 8BITMIME\r\n')
        else:
            client_socket.send(b'500 Invalid command\r\n')
            client_socket.close()


# Define POP3 functions
def pop3_server():
    # Create POP3 server socket
    pop3_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pop3_server_socket.bind((HOST, POP3_PORT))
    pop3_server_socket.listen(1)

    print('POP3 server listening on {}:{}'.format(HOST, POP3_PORT))

    while True:
        # Accept incoming POP3 connection
        client_socket, address = pop3_server_socket.accept()
        print('POP3 client connected from {}'.format(address))

        # Send initial POP3 greeting
        client_socket.send(b'+OK POP3 server ready\r\n')

        # Start POP3 handshake
        data = client_socket.recv(1024)
        if data.startswith(b'USER'):
            client_socket.send(b'+OK User accepted\r\n')
        elif data.startswith(b'PASS'):
            client_socket.send(b'+OK Pass accepted\r\n')
        else:
            client_socket.send(b'-ERR Invalid command\r\n')
            client_socket.close()


# Start SMTP and POP3 servers in separate threads
smtp_thread = threading.Thread(target=smtp_server)
pop3_thread = threading.Thread(target=pop3_server)

smtp_thread.start()
pop3_thread.start()

smtp_thread.join()
pop3_thread.join()
