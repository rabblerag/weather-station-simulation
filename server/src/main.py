import time
import os
import socket
import threading as thread
import json
from collections import deque

import packets
import logger
import database
import exceptions


max_stations = int(os.environ['MAX_STATIONS'])
max_msg_len = int(os.environ["MAX_MSG_LEN"])
server_hostname = os.environ["HOSTNAME"]
server_port = int(os.environ["SERVER_PORT"])

response = deque([])
disconnected = deque([])

def rxThread(sock_id : socket.socket, addr : tuple[str, int]) -> None:
    global response, connected
    while True:
        try:
            data = packets.read_packet(sock_id, True)
            packet = json.loads(data)
            log_data = {
                "timestamp": packet["timestamp"],
                "data": packet["data"]
            }
            logger.create_log((packet["station_id"], addr[1]), json.dumps(log_data), True)  # Store station hostname instead of IP
            database.store_data(packet["station_id"], packet["timestamp"], packet["data"])
        except exceptions.ConnectionClosedError:
            connected -= 1
            disconnected.append(sock_id)
            sock_id.close()
            return
        except Exception as e:
            exception_name = str(e.__class__).split("'")[1].split(".")[1]
            error_msg = exception_name + ": " + str(e)
            logger.create_log(addr, error_msg, False)
            response.append((sock_id, packets.create_packet(error_msg)))
        time.sleep(5)

def txThread(sock_id : socket.socket, addr : tuple[str, int]) -> None:
    global response, connected
    while True:
        if len(response) != 0:
            if response[0][0] == sock_id:
                sock_id.send(response.popleft()[1])
        if sock_id in disconnected:
            disconnected.remove(sock_id)
            return
        time.sleep(5)
 

if __name__ == "__main__":
    print("Awaiting connections...")
    server_socket = socket.socket()
    server_socket.bind((server_hostname, server_port))

    # Wait for all stations to connect
    server_socket.listen(max_stations)

    connected = 0

    while True:
        if connected == max_stations:
            time.sleep(5)
            continue
        
        conn, addr = server_socket.accept()
        
        try:
            connected_station = json.loads(packets.read_packet(conn, False))
        except Exception as e:
            exception_name = str(e.__class__).split("'")[1].split(".")[1]
            error_msg = exception_name + ": " + str(e)
            logger.create_log(addr, error_msg, False)
            denial_response = packets.create_packet(error_msg)
            conn.send(denial_response)
            conn.close()
            continue
        else:
            accept_connecion = packets.create_packet(None)
            conn.send(accept_connecion)
            logger.create_log((connected_station["station_id"], addr[1]), json.dumps({"timestamp": connected_station["timestamp"]}), True)
            database.add_stations_to_db(connected_station["station_id"], connected_station["timestamp"])
            
        connected += 1
        
        threadRX = thread.Thread(target=rxThread, args=(conn, addr))
        threadRX.daemon = True
        threadRX.start()

        threadTX = thread.Thread(target=txThread, args=(conn, addr))
        threadTX.daemon = True
        threadTX.start()


        