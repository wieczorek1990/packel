import getpass
import tomllib
from os import system

from packel import arp, up


def process(data: dict) -> None:
    password = getpass.getpass("Enter password to the SSH key: ")

    print("Processing servers...")
    for workshop, workshop_data in data["rooms"].items():
        print(f"Processing workshop: {workshop}")

        try:
            broadcast = workshop_data["broadcast"]
        except KeyError:
            print("No broadcast found.")
            continue

        print("Broadcasting: ", broadcast)
        system(f"ping -c 1 {broadcast} > /dev/null")

        try:
            servers = workshop_data["servers"]
        except KeyError:
            print("No servers found.")
            continue

        for server, server_data in servers.items():
            print(f"Processing server: {server}")

            arp_data = arp.get_arp_data()
            arp_result = arp.process_arp_data(arp_data)

            mac = server_data["mac"]
            try:
                host = arp_result[mac]
            except KeyError:
                print(f"No MAC found: {mac}")
                continue

            os = server_data["os"]
            update_class = up.get_update_for_os(os)

            update = update_class(host, password)
            update.proceed()
    print("Finished processing servers...")


def init(filename: str) -> dict:
    with open(filename, "rb") as file_descriptor:
        data = tomllib.load(file_descriptor)
    return data
