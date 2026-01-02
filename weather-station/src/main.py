from time import sleep
from os import environ

id = environ["CLIENT_ID"][-1]


if __name__ == "__main__":
    print("Connecting to server...")
    sleep(60 + int(id))
    print("Connection failed.")
    exit()