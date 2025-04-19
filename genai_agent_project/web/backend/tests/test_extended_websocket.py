"""
Extended tests for WebSocket functionality.

These tests cover more complex scenarios and edge cases 
for the WebSocket implementation.
"""

import pytest
import json
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

def test_websocket_multiple_clients(test_client, mock_agent):
    """Test multiple WebSocket clients connecting simultaneously"""
    # Open two WebSocket connections
    with test_client.websocket_connect("/ws") as websocket1:
        with test_client.websocket_connect("/ws") as websocket2:
            # Send ping from first client
            websocket1.send_json({"type": "ping"})
            
            # Expect pong for first client
            response1 = websocket1.receive_json()
            assert response1["type"] == "pong"
            
            # Send ping from second client
            websocket2.send_json({"type": "ping"})
            
            # Expect pong for second client
            response2 = websocket2.receive_json()
            assert response2["type"] == "pong"
            
            # Both connections should be active and independent

def test_websocket_invalid_json(test_client):
    """Test sending invalid JSON to WebSocket"""
    with test_client.websocket_connect("/ws") as websocket:
        # Send invalid JSON
        websocket.send_text("this is not valid json")
        
        # Expect an error response
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "message" in response

def test_websocket_missing_type(test_client):
    """Test sending JSON without a type field"""
    with test_client.websocket_connect("/ws") as websocket:
        # Send JSON without type
        websocket.send_json({"message": "Hello"})
        
        # Expect an error response
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "message" in response

def test_websocket_instruction_with_missing_params(test_client, mock_agent):
    """Test sending an instruction with missing parameters"""
    with test_client.websocket_connect("/ws") as websocket:
        # Send instruction with missing parameters
        websocket.send_json({"type": "instruction"})
        
        # Expect an error response
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "message" in response

def test_websocket_tool_with_missing_params(test_client, mock_agent):
    """Test sending a tool request with missing parameters"""
    with test_client.websocket_connect("/ws") as websocket:
        # Send tool execution with missing parameters
        websocket.send_json({"type": "tool"})
        
        # Expect an error response
        response = websocket.receive_json()
        assert response["type"] == "error"
        assert "message" in response

def test_websocket_long_running_instruction(test_client, mock_agent):
    """Test sending an instruction that takes a long time to process"""
    # Create a mock instruction method that takes time to complete
    original_process_instruction = mock_agent.process_instruction
    
    async def slow_process_instruction(*args, **kwargs):
        # Simulate a delay
        await asyncio.sleep(0.5)
        return await original_process_instruction(*args, **kwargs)
    
    # Replace the method with our slow version
    mock_agent.process_instruction = slow_process_instruction
    
    with test_client.websocket_connect("/ws") as websocket:
        # Send an instruction
        websocket.send_json({
            "type": "instruction",
            "instruction": "This will take some time",
            "context": {}
        })
        
        # Expect an acknowledgment first
        ack = websocket.receive_json()
        assert ack["type"] == "ack"
        
        # Expect a status update
        status = websocket.receive_json()
        assert status["type"] == "status"
        assert status["status"] == "processing"
        
        # Then expect the result
        result = websocket.receive_json()
        assert result["type"] == "result"
        assert "result" in result

def test_websocket_concurrent_requests(test_client, mock_agent):
    """Test sending multiple requests concurrently"""
    with test_client.websocket_connect("/ws") as websocket:
        # Send multiple requests in quick succession
        websocket.send_json({"type": "ping"})
        websocket.send_json({
            "type": "instruction",
            "instruction": "Test instruction",
            "context": {}
        })
        websocket.send_json({
            "type": "tool",
            "tool_name": "test_tool",
            "parameters": {"param1": "value1"}
        })
        
        # Collect all responses
        responses = []
        for _ in range(5):  # Expect at least 5 responses (pong, ack, status, result, ack)
            try:
                response = websocket.receive_json(timeout=1.0)
                responses.append(response)
            except:
                break
        
        # Verify we got the expected types of responses
        response_types = [r["type"] for r in responses]
        assert "pong" in response_types
        assert "ack" in response_types
        assert "status" in response_types
        assert "result" in response_types
        
        # Make sure we got at least one result
        result_responses = [r for r in responses if r["type"] == "result"]
        assert len(result_responses) > 0

def test_websocket_reconnection(test_client, mock_agent):
    """Test disconnecting and reconnecting to the WebSocket"""
    # First connection
    with test_client.websocket_connect("/ws") as websocket1:
        websocket1.send_json({"type": "ping"})
        response1 = websocket1.receive_json()
        assert response1["type"] == "pong"
    
    # Reconnect with a new connection
    with test_client.websocket_connect("/ws") as websocket2:
        websocket2.send_json({"type": "ping"})
        response2 = websocket2.receive_json()
        assert response2["type"] == "pong"

def test_websocket_large_message(test_client, mock_agent):
    """Test sending and receiving large messages"""
    # Create a large message
    large_instruction = "Generate a scene with " + " ".join(["object"] * 1000)
    
    with test_client.websocket_connect("/ws") as websocket:
        # Send a large instruction
        websocket.send_json({
            "type": "instruction",
            "instruction": large_instruction,
            "context": {}
        })
        
        # Expect an acknowledgment
        ack = websocket.receive_json()
        assert ack["type"] == "ack"
        
        # Expect a status update
        status = websocket.receive_json()
        assert status["type"] == "status"
        
        # Expect the result
        result = websocket.receive_json()
        assert result["type"] == "result"
        assert "result" in result

def test_websocket_error_propagation(test_client, mock_agent):
    """Test that errors in the processing are properly propagated"""
    # Create a mock instruction method that raises an exception
    async def failing_process_instruction(*args, **kwargs):
        raise ValueError("Simulated error in processing")
    
    # Replace the method with our failing version
    original_process_instruction = mock_agent.process_instruction
    mock_agent.process_instruction = failing_process_instruction
    
    with test_client.websocket_connect("/ws") as websocket:
        # Send an instruction
        websocket.send_json({
            "type": "instruction",
            "instruction": "This will fail",
            "context": {}
        })
        
        # Expect an acknowledgment first
        ack = websocket.receive_json()
        assert ack["type"] == "ack"
        
        # Might get a status update
        response = websocket.receive_json()
        
        # If it's a status, get the next message (error)
        if response["type"] == "status":
            response = websocket.receive_json()
        
        # Expect an error response
        assert response["type"] == "error"
        assert "message" in response
    
    # Restore the original method
    mock_agent.process_instruction = original_process_instruction
