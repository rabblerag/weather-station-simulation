import time
import socket
import os
import threading as thread
import json
from collections import deque

import packets
import exceptions

server_hostname : str = os.environ['SERVER_HOSTNAME']
server_port : int  = int(os.environ['SERVER_PORT'])
max_msg_len : int = int(os.environ['MAX_MSG_LEN'])
max_timeout : float = float(os.environ["MAX_TIMEOUT"])
id : str = os.environ["STATION_ID"]
msg_interval : int = int(os.environ["MSG_INTERVAL"])


def rxThread(sock_id : socket.socket) -> None:
    global connection_established
    while True:
        try:
            print(packets.read_packet(sock_id)) 
            time.sleep(5)
        except exceptions.ConnectionClosedError:
            sock_id.close()
            connection_established = False
            return

def txThread(sock_id : socket.socket) -> None:
    global connection_established
    while True:
        if not connection_established:
            return
        packet = packets.create_packet(True)
        sock_id.send(packet)
        time.sleep(msg_interval)


if __name__ == "__main__":
    connection_established = False
    
    while True:
        
        if connection_established:
            time.sleep(5)
    
        while not connection_established:
            time.sleep(int(id.split('station_')[-1]))

            try:
                station_socket = socket.socket()
                station_socket.connect((server_hostname, server_port))
                
                station_socket.send(packets.create_packet(False))
            except:
                print("Could not connect to server")
                time.sleep(5)
                continue
            
            try:
                response = json.loads(packets.read_packet(station_socket))
                print(response)
                if response["error"] == None:
                    connection_established = True
                else:
                    station_socket.close()
            except Exception as e:
                station_socket.close()
            
        
        print(f"Connected to server with ID {id}...")

        threadRX = thread.Thread(target=rxThread, args=(station_socket,)) # type: ignore
        threadRX.daemon = True
        threadRX.start()

        threadTX = thread.Thread(target=txThread, args=(station_socket,)) # type: ignore
        threadTX.daemon = True
        threadTX.start()
