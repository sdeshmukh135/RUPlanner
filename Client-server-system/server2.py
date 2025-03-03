import threading
import hashlib # encoding and decoding of the message
import socket #establishes connection between server and client
import sqlite3

try:
    ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("[S] server socket created")
except socket.error as err:
    print("socket error")
    exit()

server_binding = ('localhost', 9998)
ss.bind(server_binding)
ss.listen()

def check(username, password):
    conn = sqlite3.connect("mydatabase.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username,password))
    result = cursor.fetchone()
    conn.close()

    return result

def start_connection(ss):
    #msg = "Welcome to Blueprint!"
    #ss.send(msg.encode())

    data = ss.recv(1024).decode()
    username, password = data.split(",")
    
    # build login server that verifies the username and password as a valid user
    if check(username, password):
        ss.sendall("You exist and are a good person :)".encode())
    else:
        ss.sendall("What is wrong with you? Stranger danger".encode())

    #response = ss.recv(1024).decode()
    #print("[S] server message received: " + response)

while True:
    client, addr = ss.accept()
    t2 = threading.Thread(target=start_connection, args=(client,))
    t2.start()

    ss.close()
    exit()
