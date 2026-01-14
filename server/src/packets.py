import os 
import json
import hmac
import hashlib
import struct
import socket
import datetime as dt

import exceptions

max_timeout = float(os.environ["MAX_TIMEOUT"])

timezone = dt.timezone(dt.timedelta(hours=+2.0))

(min_temp, max_temp), (min_humidity, max_humidity), (min_wind_speed, max_wind_speed) = tuple(map(lambda x: tuple(map(float, x.split(','))), os.environ["METRIC_RANGES"].split('|')))

with open("/run/secrets/station-secrets") as f:
    station_keys = json.load(f)

def verify_hmac(payload : bytes, station_id : str, received_hmac : bytes) -> bool:
    try:
        secret = bytes.fromhex(station_keys[station_id])
    except KeyError:
        raise exceptions.StationKeyError("Key corresponding to station ID not found")
    calculated_hmac = hmac.new(secret, payload, hashlib.sha256).digest()

    return hmac.compare_digest(calculated_hmac, received_hmac)


def read_packet(sock_id : socket.socket) -> str:
    sock_id.settimeout(None)
    payload_len = sock_id.recv(4)

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

    data = payload['data']

    if 'temperature' in data:
        if min_temp > data['temperature'] or data['temperature'] > max_temp:
            raise exceptions.MetricRangeError("Temperature metric outside range")
    if 'humidity' in data:
        if min_humidity > data['humidity'] or data['humidity'] > max_humidity:
            raise exceptions.MetricRangeError("Temperature metric outside range")
    if 'wind_speed' in data:
        if min_wind_speed > data['wind_speed'] or data['wind_speed'] > max_wind_speed:
            raise exceptions.MetricRangeError("Temperature metric outside range")
    try:
        received_hmac = sock_id.recv(32)
    except TimeoutError as e:
        raise exceptions.ClientTimeoutError("HMAC not received following payload") from e

    if verify_hmac(raw_payload, payload["station_id"], received_hmac):
        # print("Message authenticated")
        return json.dumps(payload)
    else:
        raise exceptions.InvalidHMACError("Message doesn't match signature")

