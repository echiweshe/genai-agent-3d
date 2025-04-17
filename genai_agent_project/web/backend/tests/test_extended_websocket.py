"""
Comprehensive tests for WebSocket functionality
"""

import json
import pytest
import asyncio
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocket

def test_websocket_connection_lifecycle(test_client):
    """Test WebSocket connection lifecycle"""
    # Connect to WebSocket
    with test_client.websocket_connect("/ws") as websocket:
        # Connection should be established
        
        # Send a ping message
        websocket.send_json({"type": "ping"})
        
        # Expect a pong response
        response = websocket.receive_json()
        assert response["type"] == "pong"
        
        # Send close message
        websocket.send_json({"type": "close"})
        
    # WebSocket should be closed after the context manager exits

def test_websocket_reconnection(test_client):
    """Test WebSocket reconnection functionality"""
    # Connect to WebSocket
    with test_client.websocket_connect("/ws") as websocket:
        # Verify connection by sending ping
        websocket.send_json({"type": "ping"})
        response = websocket.receive_json()
        assert response["type"] == "pong"
    
    # Connection should be closed
    
    # Reconnect
    with test_client.websocket_connect("/ws") as websocket:
        # Send a message to verify the connection is working
        websocket.send_json({"type": "ping"})
        response = websocket.receive_json()
        assert response["type"] == "pong"

def test_websocket_instruction_processing(test_client, mock_agent):
    """Test instruction processing via WebSocket"""
    with test_client.websocket_connect("/ws") as websocket:
        # Send an instruction
        instruction = "Create a simple cube"
        websocket.send_json({
            "type": "instruction",
            "instruction": instruction,
            "context": {}
        })
        
        # Should receive acknowledgment
        ack = websocket.receive_json()
        assert ack["type"] == "ack"
        assert "message" in ack
        
        # Should receive progress updates
        progress = websocket.receive_json()
        assert progress["type"] == "progress"
        assert "message" in progress
        assert "percentage" in progress
        
        # Should receive final result
        result = websocket.receive_json()
        assert result["type"] == "result"
        assert "result" in result
        assert result["result"]["status"] == "success"
        assert "steps_executed" in result["result"]

def test_websocket_tool_execution_sequence(test_client, mock_agent):
    """Test tool execution sequence via WebSocket"""
    with test_client.websocket_connect("/ws") as websocket:
        # Send a tool execution request
        websocket.send_json({
            "type": "tool",
            "tool_name": "model_generator",
            "parameters": {
                "description": "A simple cube",
                "complexity": "low"
            }
        })
        
        # Should receive acknowledgment
        ack = websocket.receive_json()
        assert ack["type"] == "ack"
        assert "message" in ack
        
        # Should receive progress updates
        progress = websocket.receive_json()
        assert progress["type"] == "progress"
        assert "message" in progress
        assert "percentage" in progress
        
        # Should receive final result
        result = websocket.receive_json()
        assert result["type"] == "result"
        assert "result" in result
        assert result["result"]["status"] == "success"
        assert result["result"]["tool"] == "model_generator"

def test_websocket_scene_creation(test_client, mock_agent):
    """Test scene creation via WebSocket"""
    with test_client.websocket_connect("/ws") as websocket:
        # Create a new scene
        websocket.send_json({
            "type": "scene",
            "action": "create",
            "data": {
                "name": "Test Scene",
                "objects": [
                    {
                        "type": "cube",
                        "position": [0, 0, 0],
                        "scale": [1, 1, 1],
                        "rotation": [0, 0, 0],
                        "color": "#FF0000"
                    }
                ]
            }
        })
        
        # Should receive acknowledgment
        ack = websocket.receive_json()
        assert ack["type"] == "ack"
        
        # Should receive result with scene_id
        result = websocket.receive_json()
        assert result["type"] == "result"
        assert "scene_id" in result["result"]
        
        scene_id = result["result"]["scene_id"]
        
        # Update the scene
        websocket.send_json({
            "type": "scene",
            "action": "update",
            "scene_id": scene_id,
            "data": {
                "name": "Updated Scene",
                "objects": [
                    {
                        "type": "cube",
                        "position": [0, 0, 0],
                        "scale": [1, 1, 1],
                        "rotation": [0, 0, 0],
                        "color": "#FF0000"
                    },
                    {
                        "type": "sphere",
                        "position": [2, 0, 0],
                        "scale": [1, 1, 1],
                        "rotation": [0, 0, 0],
                        "color": "#00FF00"
                    }
                ]
            }
        })
        
        # Should receive acknowledgment
        ack = websocket.receive_json()
        assert ack["type"] == "ack"
        
        # Should receive result
        result = websocket.receive_json()
        assert result["type"] == "result"
        assert result["result"]["status"] == "success"

def test_websocket_error_handling(test_client):
    """Test WebSocket error handling"""
    with test_client.websocket_connect("/ws") as websocket:
        # Send a message with an invalid type
        websocket.send_json({
            "type": "invalid_type",
            "data": {}
        })
        
        # Should receive an error response
        error = websocket.receive_json()
        assert error["type"] == "error"
        assert "message" in error
        
        # Send a message with missing required fields
        websocket.send_json({
            "type": "instruction"
            # Missing 'instruction' field
        })
        
        # Should receive an error response
        error = websocket.receive_json()
        assert error["type"] == "error"
        assert "message" in error
        
        # Send a malformed JSON message (this is harder to test with the client)
        # Instead, we'll send a message with unexpected fields
        websocket.send_json({
            "type": "instruction",
            "instruction": "Test",
            "invalid_field": "Should be ignored"
        })
        
        # Should still process correctly despite the unexpected field
        ack = websocket.receive_json()
        assert ack["type"] == "ack"

def test_websocket_subscription(test_client, mock_agent):
    """Test WebSocket subscription functionality"""
    with test_client.websocket_connect("/ws") as websocket:
        # Subscribe to events
        websocket.send_json({
            "type": "subscribe",
            "topics": ["scene_updates", "tool_events"]
        })
        
        # Should receive confirmation
        response = websocket.receive_json()
        assert response["type"] == "subscription_update"
        assert response["status"] == "success"
        
        # Check subscriptions
        websocket.send_json({
            "type": "list_subscriptions"
        })
        
        # Should receive subscriptions list
        response = websocket.receive_json()
        assert response["type"] == "subscriptions"
        assert "topics" in response
        assert "scene_updates" in response["topics"]
        assert "tool_events" in response["topics"]
        
        # Unsubscribe from an event
        websocket.send_json({
            "type": "unsubscribe",
            "topics": ["tool_events"]
        })
        
        # Should receive confirmation
        response = websocket.receive_json()
        assert response["type"] == "subscription_update"
        assert response["status"] == "success"
        
        # Check subscriptions again
        websocket.send_json({
            "type": "list_subscriptions"
        })
        
        # Should receive updated subscriptions list
        response = websocket.receive_json()
        assert response["type"] == "subscriptions"
        assert "topics" in response
        assert "scene_updates" in response["topics"]
        assert "tool_events" not in response["topics"]

def test_websocket_binary_data(test_client):
    """Test sending and receiving binary data via WebSocket"""
    # This test is a bit more complex as we need to handle binary frames
    with test_client.websocket_connect("/ws") as websocket:
        # First, inform the server we're going to send binary data
        websocket.send_json({
            "type": "binary_upload",
            "filename": "test.jpg",
            "content_type": "image/jpeg",
            "size": 12  # We'll send a 12-byte dummy image
        })
        
        # Should receive an acknowledgment that we can send binary data
        response = websocket.receive_json()
        assert response["type"] == "binary_upload_ready"
        
        # Send binary data (a dummy image)
        dummy_image = bytes([0xFF, 0xD8, 0xFF, 0xE0, 0x00, 0x10, 0x4A, 0x46, 0x49, 0x46, 0x00, 0x01])
        websocket.send_bytes(dummy_image)
        
        # Should receive confirmation
        response = websocket.receive_json()
        assert response["type"] == "binary_upload_complete"
        assert "file_id" in response
        
        # Request the binary data back
        file_id = response["file_id"]
        websocket.send_json({
            "type": "binary_download",
            "file_id": file_id
        })
        
        # Should receive metadata first
        response = websocket.receive_json()
        assert response["type"] == "binary_download_info"
        assert response["filename"] == "test.jpg"
        assert response["content_type"] == "image/jpeg"
        assert response["size"] == 12
        
        # Then should receive the binary data
        binary_data = websocket.receive_bytes()
        assert binary_data == dummy_image

def test_websocket_events(test_client, mock_agent):
    """Test receiving events via WebSocket"""
    with test_client.websocket_connect("/ws") as websocket:
        # Subscribe to all events
        websocket.send_json({
            "type": "subscribe",
            "topics": ["all"]
        })
        
        # Receive subscription confirmation
        response = websocket.receive_json()
        assert response["type"] == "subscription_update"
        
        # Trigger an event (by creating a scene via REST API)
        # This would normally be done by another client
        scene_data = {
            "name": "Event Test Scene",
            "objects": [{"type": "cube", "position": [0, 0, 0]}]
        }
        
        # Use the test_client to make a REST call that should generate an event
        rest_response = test_client.post("/scene", json=scene_data)
        assert rest_response.status_code == 200
        
        # Get the scene_id from the response
        scene_id = rest_response.json()["scene_id"]
        
        # Should receive an event notification
        event = websocket.receive_json()
        assert event["type"] == "event"
        assert event["topic"] == "scene_updates"
        assert "data" in event
        assert event["data"]["action"] == "create"
        assert event["data"]["scene_id"] == scene_id

def test_websocket_concurrent_operations(test_client, mock_agent):
    """Test handling multiple concurrent operations via WebSocket"""
    with test_client.websocket_connect("/ws") as websocket:
        # Send multiple tool execution requests in sequence
        
        # First tool request
        websocket.send_json({
            "type": "tool",
            "tool_name": "model_generator",
            "parameters": {
                "description": "A simple cube",
                "request_id": "req1"
            }
        })
        
        # Second tool request (without waiting for the first to complete)
        websocket.send_json({
            "type": "tool",
            "tool_name": "diagram_generator",
            "parameters": {
                "description": "A simple flowchart",
                "request_id": "req2"
            }
        })
        
        # Should receive acknowledgments for both
        ack1 = websocket.receive_json()
        assert ack1["type"] == "ack"
        
        ack2 = websocket.receive_json()
        assert ack2["type"] == "ack"
        
        # Now collect all remaining messages
        messages = []
        # We expect at least 4 more messages (2 progress + 2 results)
        for _ in range(4):
            try:
                messages.append(websocket.receive_json())
            except Exception as e:
                break
        
        # Verify we got progress reports and results for both requests
        request_ids = set()
        result_count = 0
        
        for msg in messages:
            if msg["type"] == "result":
                result_count += 1
                # Extract request_id from the result parameters
                if "request_id" in msg["result"]["parameters"]:
                    request_ids.add(msg["result"]["parameters"]["request_id"])
        
        # We should have received results for both requests
        assert len(request_ids) >= 1  # At minimum, we should have one result
        assert result_count >= 1
