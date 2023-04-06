import socket
import urllib.request
import os

# Set up client constants
SMTP_PORT = 25
POP3_PORT = 110
HOST = 'localhost'  # '15.204.245.120'
CLIENT_DOMAIN = '348.edu'
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
def smtp_client(sender, receiver, subject, message):
    # Connect to SMTP server socket
    smtp_client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    smtp_client_socket.connect((HOST, SMTP_PORT))

    # Receive SMTP greeting from server
    data = smtp_client_socket.recv(1024)
    print(data.decode())

    # Send EHLO command to start SMTP handshake
    smtp_client_socket.send('HELO {}\r\n'.format(CLIENT_DOMAIN).encode())
    data = smtp_client_socket.recv(1024)
    print(data.decode())

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
    smtp_client_socket.send(b'QUIT\r\n');
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

"""
def user_exists(user_input):
    if os.path.isdir(user_input):
        return True
    else:
        return False


def register_user(user_input, password_input):
    # make user directory
    os.mkdir(user_input)

    # make credentials file
    with open(user_input + '/credentials.txt', 'w') as file:
        file.write('username:' + user_input + '\n')
        file.write('password:' + password_input + '\n')

    # make mail folder
    os.mkdir(user_input + '/mail')

    return True


def run_authenticate(user_input, password_input):
    credentials_file = user_input + '/credentials.txt'
    print(f"credentials_file: {credentials_file}")
    print('running authenticate!')

    # check if the cred file exists
    if not os.path.isfile(credentials_file):
        print('file doesnt exist!')
        return False

    print('file exists')
    # read stored creds from file
    with open(credentials_file, 'r') as file:
        print('opening to read creds!')
        stored_username = file.readline().strip().split(':')[1]
        print(f'stored user: {stored_username}')
        stored_pass = file.readline().strip().split(':')[1]
        print(f'stored pass: {stored_pass}')

    # compare stored cred to input
    if user_input == stored_username and password_input == stored_pass:
        return True
    else:
        return False


authenticated = False
register = False
while True:
    if not authenticated or not register:
        start_choice = input('Register or Login (R/L): ')

    if start_choice.lower() == 'r':
        register = True

    if register:
        while True:
            username = input('Enter Desired User Name: ')
            if user_exists(username):
                print('User already exists. Please choose another username.')
            else:
                password = input('Enter Desired Password:')
                register_user(username, password)
                register = False
                break

    if start_choice == 'l' and not authenticated:
        choice = input("Enter User:")
        USERNAME = choice
        choice = input("Enter Password:")
        PASSWORD = choice
        # authenticate METHOD here TODO
        while True:
            if run_authenticate(USERNAME, PASSWORD):
                break
            else:
                print('Wrong info!')
                choice = input("Enter User:")
                USERNAME = choice
                choice = input("Enter Password:")
                PASSWORD = choice
        authenticated = True
        print(f"Welcome {USERNAME}")

    if authenticated:
        choice = input("Enter 'send' or 'mail':")
        if choice == 'send':
            sender = USERNAME
            receiver = input('To user: ')
            subject = input('Enter email subject: ')
            message = input('Enter email message: ')
            while True:
                if not user_exists(username):
                    print('sent.')
                    break
                else:
                    print('sent')
                    break
            smtp_client('test@348.edu', 'yo yo', 'this is a test message!')
        if choice == 'mail':
            print('implement pop here')
"""

user_inputted = False
done = False
while not done:
    if not user_inputted:
        username_input = input('Enter Username: ')
        if '@' not in username_input:
            print("please enter a valid email!")
            continue
        print(f'Hello {username_input}!')

    user_inputted = True
    y_n = input('Do you wish to send (Y/N): ')
    if y_n.lower() == 'y':
        receiver = input('Enter receiver: ')
        subject = input('Enter subject: ')
        message = input('Enter message: ')
        smtp_client(username_input, receiver, subject, message)
    else:
        print('Bye!')
        done = True
        break

# Run Loop
# create connection ^ ^, send email
# ||
# create connection ^ ^, check email
# Close connection
