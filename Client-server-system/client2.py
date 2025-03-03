import threading
import socket

try:
    cs = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("[C] client socket created")
except socket.error as err:
    print("socket error")
    exit()

server_binding = ('localhost', 9998)
cs.connect(server_binding) # connecting to a server that is listening

username = input("Enter your username: ")
password = input("Enter your password: ")
cs.sendall(f"{username},{password}".encode('utf-8'))

data_from_server = cs.recv(1024)
message = data_from_server.decode('utf-8')
print(message)
#cs.send(input("response here: ").encode())

cs.close()
exit()