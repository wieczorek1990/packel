#!/usr/bin/env python3
# Dumps the TOML servers file as JSON.
import json
import sys
import tomli as tomllib

if len(sys.argv) != 2:
    print("Usage:\tvalidate.py servers.toml")
    sys.exit(1)

filepath = sys.argv[1]
with open(filepath, "rb") as f:
    data = tomllib.load(f)
    print(data)

dump = json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)

print(dump)
