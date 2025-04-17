"""
Tests for the WebSocket functionality
"""

import json
import pytest
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

def test_websocket_connection(test_client):
    """Test WebSocket connection"""
    with test_client.websocket_connect("/ws") as websocket:
        # Send a ping message
        websocket.send_json({"type": "ping"})
        
        # Expect a pong response
        response = websocket.receive_json()
        assert response["type"] == "pong"

def test_websocket_instruction(test_client, mock_agent):
    """Test sending an instruction via WebSocket"""
    with test_client.websocket_connect("/ws") as websocket:
        # Send an instruction
        websocket.send_json({
            "type": "instruction",
            "instruction": "Create a test scene",
            "context": {}
        })
        
        # Expect an acknowledgment
        ack = websocket.receive_json()
        assert ack["type"] == "ack"
        assert "message" in ack
        
        # Wait for the result (this will be processed in a background task)
        # In a real test, we might need to add a timeout or retry logic
        result = websocket.receive_json()
        assert result["type"] == "result"
        assert "result" in result
        assert result["result"]["status"] == "success"

def test_websocket_tool_execution(test_client, mock_agent):
    """Test executing a tool via WebSocket"""
    with test_client.websocket_connect("/ws") as websocket:
        # Send a tool execution request
        websocket.send_json({
            "type": "tool",
            "tool_name": "test_tool",
            "parameters": {"param1": "value1"}
        })
        
        # Expect an acknowledgment
        ack = websocket.receive_json()
        assert ack["type"] == "ack"
        assert "message" in ack
        
        # Wait for the result (this will be processed in a background task)
        result = websocket.receive_json()
        assert result["type"] == "result"
        assert "result" in result
        assert result["result"]["status"] == "success"
        assert result["result"]["tool"] == "test_tool"

def test_websocket_unknown_message(test_client):
    """Test sending an unknown message type via WebSocket"""
    with test_client.websocket_connect("/ws") as websocket:
        # Send an unknown message type
        websocket.send_json({
            "type": "unknown_type",
            "data": "test"
        })
        
        # Expect an error response
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "message" in response
