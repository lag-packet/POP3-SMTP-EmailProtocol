import socket
import threading

# Set up server constants
SMTP_PORT = 25
POP3_PORT = 110
HOST = 'localhost' #'15.204.245.120'


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
        client_socket.send('220 {} ESMTP server ready \r\n'.format(HOST).encode())

        # SMTP command processing loop
        while True:
            try:
                data = client_socket.recv(1024).strip()
                if not data:
                    break

                # process SMTP commands
                if data.startswith(b'EHLO'):
                    print(f'DEBUG smtp command1: {data.split()[1].decode()}')
                    client_socket.send('250-{} greets {}\r\n'.format(HOST, address[0]).encode())
                    #client_socket.send(b'250-PIPELINING\r\n')
                    #client_socket.send(b'250-ENHANCEDSTATUSCODES\r\n')
                    #client_socket.send(b'250 8BITMIME\r\n')
                elif data.startswith(b'QUIT'):
                    # handle QUIT command
                    client_socket.send(b'221 Bye\r\n')
                    client_socket.close()
                    break
                else:
                    client_socket.send(b'500 Invalid command\r\n')
            except (ConnectionResetError, ConnectionAbortedError) as e:
                print(f"Connection error: {e}")
                client_socket.close()
                break


# Define POP3 functions
def pop3_server():
    # create POP3 server socket
    pop3_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pop3_server_socket.bind((HOST, POP3_PORT))
    pop3_server_socket.listen(1)

    print(f'POP3 server listening on {HOST}:{POP3_PORT}')

    while True:
        # accept incoming POP3 connection
        client_socket, address = pop3_server_socket.accept()
        print(f'POP3 client connected from {address}')

        # send initial POP3 greeting
        client_socket.send(b'+OK POP3 server ready\r\n')

        # POP3 command processing loop
        while True:
            try:
                data = client_socket.recv(1024).strip()
                if not data:
                    break

                # process POP3 commands
                if data.startswith(b'USER'):
                    # USER command
                    print(f'User processed:{data.split()[1].decode()}')
                    client_socket.send(b'+OK User accepted\r\n')
                elif data.startswith(b'PASS'):
                    # PASS command
                    print(f'Password processed:{data.split()[1].decode()}')
                    client_socket.send(b'+OK Pass accepted\r\n')
                elif data.startswith(b'LIST'):
                    # LIST command
                    print(
                        'List command processed, sending that there is 1 message of size 100 bytes in inbox')
                    client_socket.send(b'+OK 1 messages:\r\n')
                    client_socket.send(b'1 100\r\n')
                    client_socket.send(b'.\r\n')
                elif data.startswith(b'QUIT'):
                    # handle QUIT command
                    client_socket.send(b'+OK Bye\r\n')
                    client_socket.close()
                    break
                else:
                    client_socket.send(b'-ERR Unknown command\r\n')
            except (ConnectionResetError, ConnectionAbortedError) as e:
                print(f"Connection error: {e}")
                client_socket.close()
                break


# Start SMTP and POP3 servers in separate threads
smtp_thread = threading.Thread(target=smtp_server)
pop3_thread = threading.Thread(target=pop3_server)

smtp_thread.start()
pop3_thread.start()

smtp_thread.join()
pop3_thread.join()
