import os
import tomllib
from os import system


def process(data: dict) -> None:
    print("Processing servers...")
    for server, information in data["servers"].items():
        print(f"Processing server: {server}")
        broadcast = information["broadcast"]
        system(f"ping -c 1 {broadcast} > /dev/null")
        output = os.popen("arp -a").read()

    print("Finished processing servers...")


def init(filename: str) -> dict:
    with open(filename, "rb") as file_descriptor:
        data = tomllib.load(file_descriptor)
    return data
