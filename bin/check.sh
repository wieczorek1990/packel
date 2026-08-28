#!/bin/sh
# Checks and fixes code.

ruff check --fix --unsafe-fixes ./bin ./packel/src
