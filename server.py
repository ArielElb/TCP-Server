import socket
import os
import sys
import os.path
from os import path


def fileName(line):
    names = line.split(' ')
    name = names[1]
    fName = name[1:]
    return fName


def check_conn_status(list):
    if 'Connection: close' in list:
        return 'close'
    if 'Connection: keep-alive' in list:
        return 'keep-alive'


# get the path
def getPath(fName):
    if fName.startswith("files"):
        return fName
    if fName == '' or fName == '/':
        return fName + 'files/index.html'
    else:
        return 'files/' + fName


# send image to the client with tcp socket
def redirect(client_socket):
    data = 'HTTP/1.1 301 Moved Permanently\nConnection: close\nLocation: /result.html\r\n\r\n'
    client_socket.send(data.encode())
    return 'close'


def send_img(client_socket, filePath, connStatus):
    with open(filePath, 'rb') as file:
        fileContent = file.read()
        data = f'HTTP/1.1 200 OK\nConnection:{connStatus} \nContent-Length: ' + str(
            len(fileContent)) + '\n\n'
        encodeData = data.encode()
        client_socket.send(encodeData + fileContent)


def send_default_data(client_socket, filePath, connStatus):
    with open(filePath, 'r', encoding='utf-8') as file:
        fileContent = file.read()
        data = 'HTTP/1.1 200 OK\nConnection: {conn}\nContent-Length:{length}\n\n {fileContent}'.format(
            conn=connStatus,
            length=os.path.getsize(filePath), fileContent=fileContent)
        client_socket.send(data.encode('utf-8'))


def error_404(client_socket, connStatus):
    data = 'HTTP/1.1 404 Not Found\nConnection: {conn}\r\n\r\n'.format(
        conn="close")
    connStatus = 'close'
    client_socket.send(data.encode())
    return connStatus


def check_if_finished(data):
    if data.endswith('\r\n\r\n'):
        return True
    return False


def run_server():
    # Create a TCP/IP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Bind the socket to the port
    server.bind(('', int(sys.argv[1])))
    # Listen for incoming connections
    server.listen(5)

    while True:
        # Wait for a connection
        client_socket, client_address = server.accept()
        while True:
            try:
                client_socket.settimeout(1)
                data = client_socket.recv(4096)
                print(data.decode('utf-8'))
                if not data:
                    client_socket.close()
                    break
                fileLines = data.decode('utf-8').splitlines()
                filePath = getPath(fileName(fileLines[0]))
                ext = os.path.splitext(filePath)[-1].lower()
                connStatus = check_conn_status(fileLines)
                # if the path is files/redirect
                if filePath == 'files/redirect':
                    connStatus = redirect(client_socket)
                elif path.exists(filePath):
                    # open images as binary file.
                    if ext == '.jpg' or ext == '.ico' or ext == '.png':
                        send_img(client_socket, filePath, connStatus)
                    else:
                        send_default_data(client_socket, filePath, connStatus)
                # file isn't found - send 404 error.
                else:
                    connStatus = error_404(client_socket, connStatus)

                if connStatus == "close":
                    client_socket.close()
                    break
            except socket.timeout:
                client_socket.close()
                break


def main():
    run_server()


if __name__ == "__main__":
    main()
