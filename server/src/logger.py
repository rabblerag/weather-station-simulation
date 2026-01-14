import datetime as dt
import json
import os

log_level = os.environ["LOG_LEVEL"]

timezone = dt.timezone(dt.timedelta(hours=+2.0))

def create_log(addr : tuple[str, int], value : str, isValid: bool) -> None:
    log = {
        "address": f"{addr[0]}:{addr[1]}",
        "timestamp": dt.datetime.now(timezone).isoformat(),
        "data": json.loads(value) if isValid else None,
        "error": None if isValid else value
    }

    if log_level == "info":
        print(log)

    with open(f"/app/logs/{dt.date.today().isoformat()}", "a") as f:
        f.write(json.dumps(log) + "\n")
