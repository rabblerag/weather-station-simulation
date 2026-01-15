import time
import socket
from os import environ
import threading as thread
import json

import packets

server_hostname : str = environ['SERVER_HOSTNAME']
server_port : int  = int(environ['SERVER_PORT'])
max_msg_len : int = int(environ['MAX_MSG_LEN'])
id : str = environ["STATION_ID"]
msg_interval : int = int(environ["msg_interval"])

available_metrics = tuple(environ["AVAILABLE_METRICS"].split(','))

def rxThread(sock_id : socket.socket) -> None:
    data = sock_id.recv(max_msg_len).decode()
    print("From server: ", data)
    time.sleep(5)

def txThread(sock_id : socket.socket) -> None:
    while True:
        packet = packets.create_packet(available_metrics)
        sock_id.send(packet)
        time.sleep(msg_interval)


if __name__ == "__main__":
    print(f"Connecting to server with ID {id}...")


    time.sleep(5*int(id.split('station_')[-1]))

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
