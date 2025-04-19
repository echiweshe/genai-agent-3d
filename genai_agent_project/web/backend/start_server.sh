#!/bin/bash
echo "Cleaning up previous server processes and starting server..."
python cleanup_and_start.py --auto-port "$@"
