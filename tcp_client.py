import socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('127.0.0.1', 12345))
s.send(b'hello')
data = s.recv(100)
print("Server sent: ", data)
s.close()