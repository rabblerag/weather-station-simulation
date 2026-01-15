import time
import os
import socket
import threading as thread
import random as rand
import string
import json

import packets
import logger
import database


max_stations = int(os.environ['MAX_STATIONS'])
max_msg_len = int(os.environ["MAX_MSG_LEN"])
server_hostname = os.environ["HOSTNAME"]
server_port = int(os.environ["SERVER_PORT"])


def rxThread(sock_id : socket.socket, addr : tuple[str, int]) -> None:
    while True:
        try:
            data = packets.read_packet(sock_id)
            packet = json.loads(data)
            log_data = {
                "timestamp": packet["timestamp"],
                "data": packet["data"]
            }
            logger.create_log((packet["station_id"], addr[1]), json.dumps(log_data), True)  # Store station hostname instead of IP
            database.store_data(packet["station_id"], packet["timestamp"], packet["data"])
        except Exception as e:
            exception_name = str(e.__class__).split("'")[1].split(".")[1]
            error_msg = exception_name + ": " + str(e)
            logger.create_log(addr, error_msg, False)
        time.sleep(5)

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