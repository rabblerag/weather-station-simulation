import time
import socket
from os import environ
import threading as thread

server_hostname = environ['SERVER_HOSTNAME']
server_port = int(environ['SERVER_PORT'])
max_msg_len = int(environ['MAX_MSG_LEN'])
id = environ["STATION_ID"]

def rxThread(sock_id):
    data = sock_id.recv(max_msg_len).decode()
    print("From server: ", data)
    time.sleep(5)

def txThread(sock_id):
    msg = f"Sending message as {id}"
    sock_id.send(msg.encode())
    time.sleep(5*int(id.split("STATION_")[-1]))


if __name__ == "__main__":
    print(f"Connecting to server with ID {id}...")

    time.sleep(5*int(id.split("STATION_")[-1]))

    station_socket = socket.socket()
    station_socket.connect((server_hostname, server_port))

    threadRX = thread.Thread(target=rxThread, args=(station_socket,))
    threadRX.daemon = True
    threadRX.start()

    threadTX = thread.Thread(target=txThread, args=(station_socket,))
    threadTX.daemon = True
    threadTX.start()

    while True:
        time.sleep(1)
