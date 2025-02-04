#!/bin/bash

cd "$(dirname "$0")/.." || exit

poetry run python script/test_simulation.py
