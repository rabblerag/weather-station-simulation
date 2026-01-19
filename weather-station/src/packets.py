import os
import datetime as dt
import json
import hmac
import hashlib
import struct
import socket

import sensors
import exceptions


timezone = dt.timezone(dt.timedelta(hours=+2.0))

id = os.environ['STATION_ID']
max_timeout = float(os.environ["MAX_TIMEOUT"])
enable_tests = bool(os.environ.get("ENABLE_TESTS", "False"))
available_metrics = tuple(os.environ["AVAILABLE_METRICS"].split(','))

if enable_tests:
    create_hmac_error = id == "station_3"
else:
    create_hmac_error = False


with open(f"/run/secrets/station-{int(id.split('station_')[-1])}-secret") as f:
        secret = bytes.fromhex(f.read())


with open(f"/run/secrets/server-secret") as f:
        server_key = bytes.fromhex(f.read())


def verify_hmac(payload : bytes, received_hmac : bytes) -> bool:
    calculated_hmac = hmac.new(server_key, payload, hashlib.sha256).digest()

    return hmac.compare_digest(calculated_hmac, received_hmac)


def read_packet(sock_id : socket.socket) -> str:
    sock_id.settimeout(None)
    payload_len = sock_id.recv(4)
    
    if len(payload_len) == 0:
        raise exceptions.ConnectionClosedError("Connection was closed")

    if len(payload_len) != 4:
        raise exceptions.MissingHeaderFields("Invalid length field")
    
    payload_len = struct.unpack('>I', payload_len)[0]

    sock_id.settimeout(max_timeout)
    
    try:
        raw_payload = sock_id.recv(payload_len)
    except TimeoutError as e:
        raise exceptions.ClientTimeoutError("Payload not received following length field") from e

    payload = json.loads(raw_payload)
    
    if "station_id" not in payload or "timestamp" not in payload:
        raise exceptions.MissingHeaderFields("Missing identifiers in message")
    
    current_time = dt.datetime.now(timezone)
    msg_time = dt.datetime.fromisoformat(payload['timestamp'])

    if current_time - msg_time > dt.timedelta(seconds=max_timeout):
        raise exceptions.OldTimestampError("Message timestamp too old")

    try:
        received_hmac = sock_id.recv(32)
    except TimeoutError as e:
        raise exceptions.ClientTimeoutError("HMAC not received following payload") from e

    if verify_hmac(raw_payload, received_hmac):
        return json.dumps(payload)
    else:
        raise exceptions.InvalidHMACError("Message doesn't match signature")



def create_packet(has_data : bool = True) -> bytes:
    timestamp = dt.datetime.now(timezone).isoformat(timespec='seconds')

    payload : dict[str, str | dict[str, float]] = {"station_id": id, 'timestamp': timestamp}

    if has_data:
        payload["data"] = get_data()

    packet = json.dumps(payload, sort_keys=True, separators=(',',':')).encode('utf-8')

    packet = struct.pack('>I', len(packet)) + packet

    packet += generate_hmac(packet[4:])

    return packet


def generate_hmac(payload : bytes) -> bytes:
    global create_hmac_error
    
    tag = hmac.new(secret, payload, hashlib.sha256).digest()
    
    if create_hmac_error:
        create_hmac_error = not create_hmac_error
        return tag[16:]+tag[:16]

    return tag

def get_data() -> dict[str, float]:
    data = {}

    if 'temperature' in available_metrics:
        data['temperature'] = next(sensors.measure_temp())
    if 'humidity' in available_metrics:
        data['humidity'] = next(sensors.measure_humidity())
    if 'wind_speed' in available_metrics:
        data['wind_speed'] = next(sensors.measure_wind_speed())

    return data
    
    


