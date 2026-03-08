#!/usr/bin/env python3
import json
import sys
import tomllib


if len(sys.argv) != 2:
    print("Usage:\tvalidate.py servers.toml")
    sys.exit(1)

filepath = sys.argv[1]
with open(filepath, "rb") as f:
    data = tomllib.load(f)

dump = json.dumps(data, indent=4, sort_keys=True)

print(dump)
