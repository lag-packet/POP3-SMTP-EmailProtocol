import socket
import threading
import re
import os
import datetime
import mysql.connector

# Set up server constants
SMTP_PORT = 25
POP3_PORT = 110
HOST = 'localhost'  # '15.204.245.120'
MYSQL_HOST = '18.221.218.0'


# Make connection to DB
def create_db_connection():
    return mysql.connector.connect(
        host="18.221.218.0",
        user="emailClient",
        password="381Password!",
        database="emailDatabase"
    )


def authenticate_user(username):
    connection = create_db_connection()
    cursor = connection.cursor()

    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, (username,))

    result = cursor.fetchone()
    cursor.close()
    connection.close()

    return result is not None


def authenticate_password(username, password):
    connection = create_db_connection()
    cursor = connection.cursor()

    query = "SELECT * FROM users WHERE username = %s AND password = %s"
    cursor.execute(query, (username, password))

    result = cursor.fetchone()
    cursor.close()
    connection.close()

    return result is not None


def list_command(user_id):
    connection = create_db_connection()
    cursor = connection.cursor()

    query = "SELECT id, LENGTH(body) as size FROM emails WHERE user_id = %s"
    cursor.execute(query, (user_id,))

    result = cursor.fetchall()
    cursor.close()
    connection.close()

    return result


def get_emails(user_id):
    connection = create_db_connection()
    cursor = connection.cursor()

    query = "SELECT id, subject, sender, recipient, date FROM emails WHERE user_id = %s"
    cursor.execute(query, (user_id,))

    emails = cursor.fetchall()
    cursor.close()
    connection.close()

    return emails


def retr_command(user_id, email_id):
    connection = create_db_connection()
    cursor = connection.cursor()

    query = "SELECT subject, sender, body FROM emails WHERE user_id = %s AND id = %s"
    cursor.execute(query, (user_id, email_id,))

    result = cursor.fetchall()
    cursor.close()
    connection.close()

    return result[0] if result else None


def dele_command(user_id, email_id):
    connection = create_db_connection()
    cursor = connection.cursor()

    query = "DELETE FROM emails WHERE user_id = %s AND id = %s"
    cursor.execute(query, (user_id, email_id))

    connection.commit()
    affected_rows = cursor.rowcount
    cursor.close()
    connection.close()

    return affected_rows > 0

# Get specified user ID based on email from the DB.


def get_user_id(email):
    connection = create_db_connection()
    cursor = connection.cursor()

    query = "SELECT id FROM users WHERE username = %s"
    cursor.execute(query, (email,))

    result = cursor.fetchone()
    cursor.close()
    connection.close()

    return result[0] if result else None


# def make_email_file(sender, recv, subject, message):
#     print(f'*DEBUG* recv: {recv}')
#     user_folder_path = f'{recv}'
#     print(f'*DEBUG* user folder path: {user_folder_path}')

#     if os.path.isdir(user_folder_path):
#         print(f'*DEBUG* user folder exists')
#     else:
#         print(f'*DEBUG* created user folder!')
#         os.mkdir(user_folder_path)

#     email_file_path = f"{recv}/{subject}.txt"
#     print(f'*DEBUG* email file {email_file_path}')
#     print(f'*DEBUG* subject: {subject}')
#     with open(email_file_path, 'w') as file:
#         file.write('From:' + sender + '\n')
#         file.write(message)
#     print(f'*DEBUG* email filed created!')


# Insert email to db for respective user
def insert_email_to_db(sender, recv, subject, message):
    # Get recipient's user_id
    recipient_id = get_user_id(recv + '@email.com')
    print(f'rec id {recipient_id}')

    if recipient_id is None:
        print("ERR - the recipient does not exist")

        return

    # Current date and time
    current_date = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    connection = create_db_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO emails (user_id, subject, sender, recipient, date, body)
    VALUES (%s, %s, %s, %s, %s, %s);
    """

    cursor.execute(query, (recipient_id, subject, sender + '@email.com',
                           recv + '@email.com', current_date, message))
    connection.commit()
    cursor.close()
    connection.close()
    print("Email has been sent successfully.")


# Define SMTP SERVER
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
        client_socket.send(
            '220 {} ESMTP server ready \r\n'.format(HOST).encode())

        mail_from = ''
        recpt_to = ''
        # SMTP command processing loop
        while True:

            try:
                data = client_socket.recv(1024)
                if not data:
                    break

                # process SMTP commands
                if data.startswith(b'HELO'):
                    # print(f'DEBUG smtp command1: {data.split()[1].decode()}')
                    print(data.decode())
                    client_socket.send(
                        '250 Hello {}, pleased to meet you\r\n'.format(data.split()[1].decode()).encode())
                elif data.startswith(b'AUTHLOGIN'):
                    print(
                        f'AUTH LOGIN REQUEST RECEIVED, USERNAME INPUTTED: {data.split()[1].decode()}, PASSWORD INPUTTED: {data.split()[2].decode()}')
                    username = data.split()[1].decode()
                    password = data.split()[2].decode()
                    # 235 = success
                    # 535 = invalid
                    if authenticate_user(username) and authenticate_password(username, password):
                        client_socket.send(
                            b'235 2.7.0 User authentication successful\r\n')
                    else:
                        client_socket.send(
                            b'535\r\n')
                        print(f'AUTH LOGIN FAILED for {username}')
                        break
                elif data.startswith(b'MAIL FROM'):
                    print(data.decode())
                    mail_from_match = re.search(r'<([^@]+)', data.decode())
                    if mail_from_match:
                        mail_from = mail_from_match.group(1)
                    print(f'*DEBUG* mail from: {mail_from}')

                    client_socket.send(
                        '250 {} ... Sender ok\r\n'.format(
                            data.split()[1].decode()).encode()
                    )
                elif data.startswith(b'RCPT TO:'):
                    print(data.decode())
                    recpt_to_match = re.search(r'<([^@]+)', data.decode())
                    if recpt_to_match:
                        recpt_to = recpt_to_match.group(1)
                    print(f'*DEBUG* recpt to: {recpt_to}')

                    client_socket.send(
                        '250 {} ... Recipient ok\r\n'.format(
                            data.split()[1].decode()).encode()
                    )
                elif data.startswith(b'DATA'):
                    print(data.decode())
                    client_socket.send(
                        b'354 Enter mail, end with "." on a line by itself\r\n')

                    # Capture the whole message
                    message_data = bytearray()
                    while True:
                        chunk = client_socket.recv(1024)
                        if not chunk:
                            break
                        message_data.extend(chunk)
                        if message_data.endswith(b'\r\n.\r\n'):
                            break
                    # print("DEBUG")
                    mail_msg = message_data.decode()
                    mail_msg = "\r\n".join(mail_msg.rsplit("\r\n.\r\n", 1))
                    subject_match = re.search(
                        r'Subject: (.*?)\r\n\r\n', mail_msg, re.DOTALL)
                    if subject_match:
                        subject_text = subject_match.group(1)
                        print(f"Subject text: {subject_text}")
                    else:
                        print("Subject not found")
                    print(message_data.decode())

                    # Makes the mail file in the recp. mail folder
                    # make_email_file(mail_from, recpt_to, subject_text, mail_msg)
                    # insert_email_to_db(mail_from, recpt_to, subject_text, mail_msg)

                    # Remove the "Subject:" line and any text following it
                    mail_msg = re.sub(r'Subject:.*?\r\n', '',
                                      mail_msg, flags=re.DOTALL)
                    mail_msg = mail_msg.replace('\r\n', '').replace('\n', '')

                    insert_email_to_db(mail_from, recpt_to,
                                       subject_text, mail_msg)

                    client_socket.send(
                        b'250 Message accepted for delivery\r\n')
                elif data.startswith(b'QUIT'):
                    client_socket.send(
                        '221 {} closing connection\r\n'.format(HOST).encode())
                    client_socket.close()
                    break
                else:
                    client_socket.send(b'500 Invalid command\r\n')
            except (ConnectionResetError, ConnectionAbortedError) as e:
                print(f"Connection error: {e}")
                client_socket.close()
                break


# Define POP3 SERVER
def pop3_server():
    # create POP3 server socket
    pop3_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    pop3_server_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
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
                data = client_socket.recv(1024)
                if not data:
                    break
            # process POP3 commands
                # handle USER command
                if data.startswith(b'USER'):
                    try:
                        username = data.split()[1].decode()
                    except:
                        print("ERROR wrong input")
                        client_socket.close()
                        break
                    print(f'User processed: {data.split()[1].decode()}')

                    if authenticate_user(username):
                        client_socket.send(b'+OK User accepted\r\n')
                    else:
                        client_socket.send(b'-ERR User not found\r\n')
                        break
                # handle PASS command
                elif data.startswith(b'PASS'):
                    try:
                        password = data.split()[1].decode()
                    except:
                        print("ERROR wrong input")
                        client_socket.close()
                        break
                    print(f'Password processed: {data.split()[1].decode()}')
                    if authenticate_password(username, password):
                        client_socket.send(b'+OK Pass accepted\r\n')
                    else:
                        client_socket.send(b'-ERR password incorrect\r\n')
                        break
                # handle LIST command
                elif data.startswith(b'LIST'):
                    print('List command processed, fetching email list from database')
                    user_id = get_user_id(username)
                    email_list = list_command(user_id)

                    if email_list:
                        client_socket.send(
                            f'+OK {len(email_list)} messages:\r\n'.encode())
                        for email in email_list:
                            client_socket.send(
                                f'{email[0]} {email[1]}\r\n'.encode())
                        client_socket.send(b'.\r\n')
                    else:
                        client_socket.send(b'+OK 0 messages\r\n')
                # handle RETR command
                elif data.startswith(b'RETR'):
                    print('RETR command processed, fetching email body from database')
                    user_id = get_user_id(username)
                    email_id = int(data.split()[1])
                    retr_res = retr_command(user_id, email_id)
                    if retr_res:
                        client_socket.send(b'+OK\r\n')
                        print(retr_res)
                        client_socket.send(
                            f'SUBJECT: {retr_res[0]} SENDER: {retr_res[1]} BODY: {retr_res[2]}'.encode())
                        client_socket.send(b'\r\n.\r\n')
                    else:
                        client_socket.send(b'-ERR Email not found\r\n')
                # handle DELE command
                elif data.startswith(b'DELE'):
                    print(
                        'DELE command processed, email queued for deletion, will commence after QUIT command.')
                    user_id = get_user_id(username)
                    email_id = int(data.split()[1])

                    if dele_command(user_id, email_id):
                        client_socket.send(b'+OK Email deleted\r\n')
                    else:
                        client_socket.send(b'-ERR Email not found\r\n')
                # handle QUIT command
                elif data.startswith(b'QUIT'):
                    client_socket.send(b'+OK Bye\r\n')
                    client_socket.close()
                    print(f'Connection with {username} closed')
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
