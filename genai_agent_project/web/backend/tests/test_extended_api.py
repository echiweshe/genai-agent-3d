"""
Extended tests for the FastAPI backend endpoints
"""

import json
import pytest
import io
from fastapi import status, UploadFile

def test_scene_endpoints(test_client, mock_agent):
    """Test the scene management endpoints"""
    # Create a scene
    scene_data = {
        "name": "Test Scene",
        "description": "A test scene with a cube",
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
    
    response = test_client.post(
        "/scene",
        json=scene_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "scene_id" in data
    scene_id = data["scene_id"]
    
    # Get the scene
    response = test_client.get(f"/scene/{scene_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert data["scene"]["name"] == "Test Scene"
    assert len(data["scene"]["objects"]) == 1
    
    # Update the scene
    update_data = {
        "name": "Updated Test Scene",
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
    
    response = test_client.put(
        f"/scene/{scene_id}",
        json=update_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    
    # Get the updated scene
    response = test_client.get(f"/scene/{scene_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert data["scene"]["name"] == "Updated Test Scene"
    assert len(data["scene"]["objects"]) == 2
    
    # List scenes
    response = test_client.get("/scenes")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert len(data["scenes"]) >= 1
    
    # Delete the scene
    response = test_client.delete(f"/scene/{scene_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    
    # Verify the scene is deleted
    response = test_client.get(f"/scene/{scene_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_model_endpoints(test_client, mock_agent):
    """Test the model management endpoints"""
    # Generate model
    model_data = {
        "description": "A simple cube with beveled edges",
        "parameters": {
            "complexity": "low",
            "style": "geometric"
        }
    }
    
    response = test_client.post(
        "/model/generate",
        json=model_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "model_id" in data
    model_id = data["model_id"]
    
    # Get model
    response = test_client.get(f"/model/{model_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "model" in data
    assert "description" in data["model"]
    
    # List models
    response = test_client.get("/models")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "models" in data
    assert len(data["models"]) >= 1
    
    # Delete model
    response = test_client.delete(f"/model/{model_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    
    # Verify model is deleted
    response = test_client.get(f"/model/{model_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_diagram_endpoints(test_client, mock_agent):
    """Test the diagram generation endpoints"""
    # Generate diagram
    diagram_data = {
        "type": "flowchart",
        "description": "A simple workflow with three steps",
        "parameters": {
            "format": "mermaid",
            "direction": "TD"
        }
    }
    
    response = test_client.post(
        "/diagram/generate",
        json=diagram_data
    )
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "diagram_id" in data
    diagram_id = data["diagram_id"]
    
    # Get diagram
    response = test_client.get(f"/diagram/{diagram_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "diagram" in data
    
    # List diagrams
    response = test_client.get("/diagrams")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "diagrams" in data
    
    # Delete diagram
    response = test_client.delete(f"/diagram/{diagram_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    
    # Verify diagram is deleted
    response = test_client.get(f"/diagram/{diagram_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_file_operations(test_client, mock_agent):
    """Test file upload, download and management endpoints"""
    # Upload file
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
    assert "file_id" in data
    file_id = data["file_id"]
    
    # List files
    response = test_client.get("/files")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    assert "files" in data
    assert len(data["files"]) >= 1
    
    # Download file
    response = test_client.get(f"/file/{file_id}")
    assert response.status_code == status.HTTP_200_OK
    assert response.content == file_content
    
    # Delete file
    response = test_client.delete(f"/file/{file_id}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "success"
    
    # Verify file is deleted
    response = test_client.get(f"/file/{file_id}")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_error_handling(test_client):
    """Test API error handling"""
    # Non-existent endpoint
    response = test_client.get("/non_existent_endpoint")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Invalid JSON
    response = test_client.post(
        "/instruction",
        data="invalid json",
        headers={"Content-Type": "application/json"}
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Missing required field
    response = test_client.post(
        "/instruction",
        json={"context": {}}  # Missing 'instruction' field
    )
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    # Invalid tool name
    response = test_client.post(
        "/tool",
        json={"tool_name": "non_existent_tool", "parameters": {}}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Invalid scene ID
    response = test_client.get("/scene/non_existent_id")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
    # Invalid model ID
    response = test_client.get("/model/non_existent_id")
    assert response.status_code == status.HTTP_404_NOT_FOUND

def test_asyncio_handling(test_client, mock_agent):
    """Test asyncio handling in API endpoints"""
    # Test with a long-running instruction
    instruction_data = {
        "instruction": "Long running task",
        "context": {"long_running": True}
    }
    
    response = test_client.post(
        "/instruction/async",
        json=instruction_data
    )
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert data["status"] == "accepted"
    assert "task_id" in data
    
    # Get task status
    task_id = data["task_id"]
    response = test_client.get(f"/task/{task_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "status" in data
    assert data["status"] in ["pending", "running", "completed", "failed"]

def test_authentication_endpoints(test_client):
    """Test authentication endpoints if implemented"""
    # Register
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123"
    }
    
    response = test_client.post(
        "/auth/register",
        json=register_data
    )
    
    # If auth is implemented, expect success or conflict if user exists
    if response.status_code == status.HTTP_200_OK:
        data = response.json()
        assert data["status"] == "success"
        
        # Login
        login_data = {
            "username": "testuser",
            "password": "securepassword123"
        }
        
        response = test_client.post(
            "/auth/login",
            json=login_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "success"
        assert "access_token" in data
        
        # Use token for authorized request
        token = data["access_token"]
        response = test_client.get(
            "/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        
        # Logout
        response = test_client.post(
            "/auth/logout",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
