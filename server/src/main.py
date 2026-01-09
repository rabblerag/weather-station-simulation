import time
import os
import socket
import threading as thread
import random as rand
import string

import packets



max_stations = int(os.environ['MAX_STATIONS'])
max_msg_len = int(os.environ["MAX_MSG_LEN"])
server_hostname = os.environ["HOSTNAME"]
server_port = int(os.environ["SERVER_PORT"])


def rxThread(sock_id : socket.socket, addr : tuple[str, int]) -> None:
    data = packets.read_packet(sock_id)
    if data != None:
        print("From connected user: ", data)

def txThread(sock_id : socket.socket, addr : tuple[str, int]) -> None:
    msg = ''.join(rand.choices(string.ascii_lowercase, k=5))
    sock_id.send(msg.encode())
 

if __name__ == "__main__":
    print("Awaiting connection...")
    server_socket = socket.socket()
    server_socket.bind((server_hostname, server_port))

    # Wait for all stations to connect
    server_socket.listen(max_stations)

    connected = 0

    while connected < max_stations :
        conn, addr = server_socket.accept()
        
        threadRX = thread.Thread(target=rxThread, args=(conn, addr))
        threadRX.daemon = True
        threadRX.start()

        threadTX = thread.Thread(target=txThread, args=(conn, addr))
        threadTX.daemon = True
        threadTX.start()

    while True:
        time.sleep(1)