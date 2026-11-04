#!/usr/bin/env python3
# Dumps the TOML servers file as JSON.
import json
import sys
import tomllib

if len(sys.argv) != 2:
    print("Usage:\tvalidate.py data/servers.toml")
    sys.exit(1)

filepath = sys.argv[1]
with open(filepath, "rb") as f:
    data = tomllib.load(f)

dump = json.dumps(data, indent=4, sort_keys=True, ensure_ascii=False)

print(dump)
