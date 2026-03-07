import tomllib


def init(filename):
    with open(filename, "rb") as f:
        data = tomllib.load(f)
        print(data)
