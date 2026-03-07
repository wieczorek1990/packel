import sys
import tomllib


def init():
    if len(sys.argv) != 1:
        exit(1)

    filename = sys.argv[1]
    with open(filename, "rb") as f:
        data = tomllib.load(f)
        print(data)


init()
