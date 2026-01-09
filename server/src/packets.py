import os 
import json
import hmac
import hashlib
import struct
import socket
import datetime as dt

timezone = dt.timezone(dt.timedelta(hours=+2.0))

min_temp = float(os.environ["MIN_TEMP"])
max_temp = float(os.environ["MAX_TEMP"])
max_humidity = float(os.environ["MAX_HUMIDITY"])
max_wind_speed = float(os.environ["MAX_WIND_SPEED"])

with open("/run/secrets/station-secrets") as f:
    station_keys = json.load(f)

def verify_hmac(payload : bytes, station_id : str, received_hmac : bytes) -> bool:
    try:
        secret = bytes.fromhex(station_keys[station_id])
    except KeyError:
        print("Key corresponding to station ID not found")
        return False
    calculated_hmac = hmac.new(secret, payload, hashlib.sha256).digest()

    return hmac.compare_digest(calculated_hmac, received_hmac)


def read_packet(sock_id : socket.socket) -> dict[str, str | dict[str, float]] | None:
    payload_len = sock_id.recv(4)

    if payload_len != 4:
        print("Invalid length field")
        return None
    
    payload_len = struct.unpack('>I', payload_len)[0]

    raw_payload = sock_id.recv(payload_len)

    try:
        payload = json.loads(raw_payload)
    except json.JSONDecodeError:
        print("Invalid JSON received")
        return None
    
    if "station_id" not in payload or "timestamp" not in payload:
        print("Missing identifiers in message")
        return None
    
    current_time = dt.datetime.now(timezone)
    msg_time = dt.datetime.fromisoformat(payload['timestamp'])

    if current_time - msg_time > dt.timedelta(seconds=5):
        print("Message too old")
        return None

    data = payload['data']

    if 'temperature' in data:
        if min_temp > data['temperature'] or data['temperature'] > max_temp:
            print("Invalid data")
            return None
    if 'humidity' in data:
        if 0 > data['humidity'] or data['humidity'] > max_humidity:
            print("Invalid data")
            return None
    if 'wind_speed' in data:
        if 0 > data['wind_speed'] or data['wind_speed'] > max_wind_speed:
            print("Invalid data")
            return None
    
    received_hmac = sock_id.recv(32)

    if verify_hmac(raw_payload, payload["station_id"], received_hmac):
        print("Message authenticated")
        return payload
    else:
        print("Message doesn't match signature")
        return None

