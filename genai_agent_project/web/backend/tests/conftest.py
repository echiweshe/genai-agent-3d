"""
Pytest configuration file for FastAPI backend tests
"""

import os
import sys
import pytest
from fastapi.testclient import TestClient

# Add parent directory to path for imports
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_dir)

# Import app and create test client
from web.backend.main import app

# Mock dependencies
class MockRedisMessageBus:
    """Mock Redis Message Bus for testing"""
    
    async def connect(self):
        """Mock connect method"""
        return True
    
    async def disconnect(self):
        """Mock disconnect method"""
        return True
    
    async def ping(self):
        """Mock ping method"""
        return True
    
    async def call_rpc(self, method, params):
        """Mock RPC call method"""
        if method == 'service:get_by_name':
            return {'service': {}}
        return {}
    
    async def publish(self, topic, message):
        """Mock publish method"""
        return True

class MockGenAIAgent:
    """Mock GenAI Agent for testing"""
    
    async def process_instruction(self, instruction, context=None):
        """Mock process_instruction method"""
        return {
            'status': 'success',
            'message': f'Processed instruction: {instruction}',
            'steps_executed': 1,
            'results': [{
                'step': 1,
                'description': 'Test step',
                'tool': 'test_tool',
                'result': {
                    'status': 'success',
                    'message': 'Test result'
                }
            }]
        }
    
    async def close(self):
        """Mock close method"""
        return True
    
    class ToolRegistry:
        """Mock Tool Registry"""
        
        def get_tools(self):
            """Mock get_tools method"""
            return [
                type('Tool', (), {'name': 'test_tool', 'description': 'Test tool'}),
                type('Tool', (), {'name': 'model_generator', 'description': 'Creates 3D models'})
            ]
        
        async def execute_tool(self, tool_name, parameters):
            """Mock execute_tool method"""
            return {
                'status': 'success',
                'message': f'Executed tool: {tool_name}',
                'tool': tool_name,
                'parameters': parameters
            }
    
    tool_registry = ToolRegistry()

@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app"""
    with TestClient(app) as client:
        yield client

@pytest.fixture
def mock_agent(monkeypatch):
    """Create and inject a mock GenAI Agent"""
    agent = MockGenAIAgent()
    monkeypatch.setattr('web.backend.main.agent', agent)
    return agent

@pytest.fixture
def mock_redis_bus(monkeypatch):
    """Create and inject a mock Redis Message Bus"""
    redis_bus = MockRedisMessageBus()
    monkeypatch.setattr('web.backend.main.redis_bus', redis_bus)
    return redis_bus
