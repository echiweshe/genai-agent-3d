"""
Tests for the FastAPI backend endpoints
"""

import json
import pytest
from fastapi import status

def test_root_endpoint(test_client):
    """Test the root endpoint"""
    response = test_client.get("/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {"message": "GenAI Agent 3D API"}

def test_status_endpoint(test_client, mock_agent, mock_redis_bus):
    """Test the status endpoint"""
    response = test_client.get("/status")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["status"] == "ok"
    assert "agent" in data
    assert "redis" in data
    assert "version" in data

def test_instruction_endpoint(test_client, mock_agent):
    """Test the instruction endpoint"""
    instruction_data = {
        "instruction": "Create a simple cube",
        "context": {"test": True}
    }
    
    response = test_client.post(
        "/instruction",
        json=instruction_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["status"] == "success"
    assert "message" in data
    assert "steps_executed" in data
    assert "results" in data

def test_tool_endpoint(test_client, mock_agent):
    """Test the tool execution endpoint"""
    tool_data = {
        "tool_name": "test_tool",
        "parameters": {"param1": "value1"}
    }
    
    response = test_client.post(
        "/tool",
        json=tool_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["status"] == "success"
    assert data["tool"] == "test_tool"
    assert data["parameters"] == {"param1": "value1"}

def test_tools_endpoint(test_client, mock_agent):
    """Test the tools listing endpoint"""
    response = test_client.get("/tools")
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["status"] == "success"
    assert "tools" in data
    assert len(data["tools"]) == 2
    
    # Check that the tools match the expected values
    tool_names = [tool["name"] for tool in data["tools"]]
    assert "test_tool" in tool_names
    assert "model_generator" in tool_names

def test_config_get_endpoint(test_client):
    """Test the config GET endpoint"""
    response = test_client.get("/config")
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["status"] == "success"
    assert "config" in data

def test_config_post_endpoint(test_client):
    """Test the config POST endpoint"""
    config_data = {
        "section": "test_section",
        "key": "test_key",
        "value": "test_value"
    }
    
    response = test_client.post(
        "/config",
        json=config_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["status"] == "success"
    assert "message" in data

def test_upload_endpoint(test_client):
    """Test the file upload endpoint"""
    # Create a test file
    file_content = b"test file content"
    
    response = test_client.post(
        "/upload",
        files={"file": ("test.txt", file_content, "text/plain")}
    )
    
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["status"] == "success"
    assert "filename" in data
    assert data["filename"] == "test.txt"
