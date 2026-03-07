import tomllib


def process(data: dict) -> None:
    print("Processing servers...")
    ...
    print("Finished processing servers...")


def init(filename: str) -> dict:
    with open(filename, "rb") as file_descriptor:
        data = tomllib.load(file_descriptor)
    return data
