#!/bin/sh
# Runs the test suite.

export PYTHONPATH="${PWD}/packel/src:$PYTHONPATH"
python3 -m unittest discover -s packel/tests -v
