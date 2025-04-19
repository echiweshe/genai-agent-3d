#!/bin/bash
echo "Running WebSocket tests for GenAI Agent 3D"
cd "$(dirname "$0")/web"
python run_all_tests.py --manual-websocket --test-mode "$@"
