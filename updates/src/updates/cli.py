import sys

from updates.servers import init, process


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage:\tservers.py servers.toml")
        sys.exit(1)

    print("Starting reading requested...")

    filename = sys.argv[1]
    data = init(filename)
    process(data)

    print("Done.")
