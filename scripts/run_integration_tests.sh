#!/usr/bin/env bash

make clean
uv sync

while true
do
  echo "Running integration tests..."
  time uv run pytest -m "integration" "$@"
  echo "Tests finished."
done
