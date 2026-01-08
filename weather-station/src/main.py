import time
import socket
from os import environ
import threading as thread
import json

import sensors


server_hostname = environ['SERVER_HOSTNAME']
server_port = int(environ['SERVER_PORT'])
max_msg_len = int(environ['MAX_MSG_LEN'])
id = environ["STATION_ID"]

def rxThread(sock_id):
    data = sock_id.recv(max_msg_len).decode()
    print("From server: ", data)
    time.sleep(5)

def txThread(sock_id):
    msg = json.dumps({"station_id": id, "timestamp": "2025-01-09T00:00:00", "data": {
        "temperature": sensors.measure_temp().__next__(), "humidity": sensors.measure_humidity().__next__(),
        "wind_speed": sensors.measure_wind_speed().__next__()
    }})
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
