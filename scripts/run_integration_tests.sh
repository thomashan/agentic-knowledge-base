#!/usr/bin/env bash

while true
do
  echo "Running integration tests..."
  uv sync
  time uv run pytest -m "integration"
  make fix-ruff
  echo "Tests finished. Waiting 5 seconds before next run..."
done
