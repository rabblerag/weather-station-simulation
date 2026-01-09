import os
import datetime as dt
import json
import hmac
import hashlib
import struct

import sensors

timezone = dt.timezone(dt.timedelta(hours=+2.0))

id = os.environ['STATION_ID']

with open(f"/run/secrets/station-{int(id.split('STATION_')[-1])}-secret") as f:
        secret = bytes.fromhex(f.read())


def create_packet(available_metrics : tuple[str, ...]=('temperature', 'humidity', 'wind_speed')) -> bytes:
    timestamp = dt.datetime.now(timezone).isoformat(timespec='seconds')

    data = get_data(available_metrics)

    packet = json.dumps({"station_id": id, 'timestamp': timestamp, 'data': data}, sort_keys=True, separators=(',',':')).encode('utf-8')

    packet = struct.pack('>I', len(packet)) + packet

    packet += generate_hmac(packet[4:])

    return packet


def generate_hmac(payload : bytes) -> bytes:
    tag = hmac.new(secret, payload, hashlib.sha256).digest()

    return tag

def get_data(available_metrics : tuple[str, ...]=('temperature', 'humidity', 'wind_speed')) -> dict[str, float]:
    data = {}

    if 'temperature' in available_metrics:
        data['temperature'] = next(sensors.measure_temp())
    if 'humidity' in available_metrics:
        data['humidity'] = next(sensors.measure_humidity())
    if 'wind_speed' in available_metrics:
        data['wind_speed'] = next(sensors.measure_wind_speed())

    return data
    
    


