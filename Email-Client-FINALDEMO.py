import socket
import urllib.request

# Set up client constants
SMTP_PORT = 25
POP3_PORT = 110
HOST = 'localhost'  # '15.204.245.120'
CLIENT_DOMAIN = '348.edu'
USERNAME = 'client_username'
PASSWORD = 'client_password'


# receive data function takes in a large amount of data, to not overflow buffer, waits until it finishes receiving data
# and ends when '.' message is sent from the server.
def receive_data(sock):
    chunks = []
    while True:
        chunk = sock.recv(8192)
        if not chunk:
            break
        chunks.append(chunk)
        if b'\r\n.\r\n' in chunk:
            break
    return b''.join(chunks).decode()


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

    # Send EHLO command to start SMTP handshake
    smtp_client_socket.send('HELO {}\r\n'.format(CLIENT_DOMAIN).encode())
    data = smtp_client_socket.recv(1024)
    print(data.decode(), end='')

    print("LOGIN: ")
    auth_login_input = input(
        'Enter in this format (USERNAME PASSWORD): ')
    # password = input('Enter Password: ')
    try:
        sender = auth_login_input.split()[0]
    except:
        print("ERROR wrong input")
        return False

    try:
        password = auth_login_input.split()[1]
    except:
        print("ERROR wrong input")
        return False

    # Send AUTH LOGIN command to start SMTP handshake
    smtp_client_socket.send(
        'AUTHLOGIN {}\r\n'.format(auth_login_input).encode())
    data = smtp_client_socket.recv(1024)
    print(data.decode())
    if data == b'535\r\n':
        print('535 Authentication credentials invalid')
        print('Please enter a correct username or password and try again.')
        return False

    receiver = input('Enter recipient: ')
    subject = input('Enter email subject: ')
    message = input('Enter email body: ')

    # Send MAIL FROM command to SMTP Server
    smtp_client_socket.send('MAIL FROM: <{}>\r\n'.format(sender).encode())
    data = smtp_client_socket.recv(1024)
    print(data.decode())

    # Send RCPT TO command to SMTP server
    smtp_client_socket.send('RCPT TO: <{}>\r\n'.format(receiver).encode())
    data = smtp_client_socket.recv(1024)
    print(data.decode())

    # Send DATA command to SMTP server
    smtp_client_socket.send(b'DATA\r\n')
    data = smtp_client_socket.recv(1024)
    print(data.decode())

    # Send email message
    send_message = "Subject: {}\r\n\r\n{}".format(subject, message)
    smtp_client_socket.send(send_message.encode())

    # Send end of message
    smtp_client_socket.send(b'\r\n.\r\n')
    data = smtp_client_socket.recv(1024)
    print(data.decode())

    # Send QUIT command
    smtp_client_socket.send(b'QUIT\r\n')
    data = smtp_client_socket.recv(1024)
    print(data.decode())

    # Close SMTP connection
    smtp_client_socket.close()
    print("smtp closed")


# Define POP3 functions
def pop3_client():
    # Connect to POP3 server socket
    print("Connecting to POP3 Server...")
    pop3_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pop3_client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    pop3_client_socket.connect((HOST, POP3_PORT))

    # Receive POP3 greeting from server
    data = pop3_client_socket.recv(1024)
    print(data.decode(), end='')
    print("LOGIN: ")
    USERNAME = input("Please enter your username: ")
    PASSWORD = input("Please enter your password: ")

    if len(USERNAME) == 0 or len(PASSWORD) == 0:
        print("ERROR wrong input detected")
        return False

    # Send USER command to start POP3 handshake
    pop3_client_socket.send('USER {}\r\n'.format(USERNAME).encode())
    data = pop3_client_socket.recv(1024)

    print(data.decode(), end='')
    if data == b'-ERR User not found\r\n':
        print('Please enter a correct username or password and try again.')
        return False

    # Send PASS command to continue POP3 handshake
    pop3_client_socket.send('PASS {}\r\n'.format(PASSWORD).encode())
    data = pop3_client_socket.recv(1024)
    print(data.decode(), end='')

    while True:
        print("Menu:")
        print("1. LIST Command")
        print("2. RETR Command")
        print("3. DELE command")
        print("4. QUIT Command")

        choice = input("Enter your choice (1-4): ")
        print("-----------------------")

        if choice == '1':
            # send LIST command to list messages
            pop3_client_socket.send(b"LIST\r\n")
            data = receive_data(pop3_client_socket)
            print(data)
        elif choice == '2':
            # send RETR command to retrieve a message
            message_number = input("Enter the message number to retrieve: ")
            pop3_client_socket.send(f"RETR {message_number}\r\n".encode())
            # Increase the buffer size for larger emails
            data = receive_data(pop3_client_socket)
            print(data)
            # data = pop3_client_socket.recv(1024)
            # print(data.decode())
        elif choice == '3':
            message_number = input("Enter the message number to delete: ")
            print('Sending DELE command...')
            pop3_client_socket.send(f"DELE {message_number}\r\n".encode())
            response = pop3_client_socket.recv(1024)
            print(f'DELE response: {response.decode()}')
        elif choice == '4':
            # send QUIT command to log out and close the connection
            pop3_client_socket.send(b"QUIT\r\n")
            data = pop3_client_socket.recv(1024)
            print(data.decode())

            # Close POP3 connection
            pop3_client_socket.close()
            print('client closed')
            break
        else:
            # Invalid input
            print("Invalid choice. Please try again.")


done = False
while not done:
    s_r = input('Send(s) or Read email(r) or Quit(any input): ')
    if s_r.lower() == 's':
        smtp_client()
        done = True
    elif s_r.lower() == 'r':
        pop3_client()
        done = True
        break
    else:
        print('Bye!')
        done = True
        break

# Run Loop
# create connection ^ ^, send email
# ||
# create connection ^ ^, check email
# Close connection
