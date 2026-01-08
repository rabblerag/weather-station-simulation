from time import sleep
from os import environ

id = environ["STATION_ID"]

if __name__ == "__main__":
    print(f"Connecting to server with ID {id}...")
    sleep(60 + int(id.split("STATION_")[-1]))
    print("Connection failed.")
    exit()