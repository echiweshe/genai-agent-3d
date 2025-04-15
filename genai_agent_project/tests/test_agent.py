"""
Tests for the GenAI Agent
"""

import unittest
import asyncio
import os
import sys
import logging
from unittest.mock import MagicMock, patch

# Add parent directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from genai_agent.agent import GenAIAgent
from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.services.llm import LLMService
from genai_agent.services.memory import MemoryService
from genai_agent.core.task_manager import TaskManager
from genai_agent.core.context_manager import ContextManager
from genai_agent.tools.registry import ToolRegistry, Tool

# Disable logging during tests
logging.disable(logging.CRITICAL)

class MockTool(Tool):
    """Mock tool for testing"""
    
    def __init__(self):
        super().__init__(name="mock_tool", description="Mock tool for testing")
        self.execute_called = False
    
    async def execute(self, parameters):
        self.execute_called = True
        return {"status": "success", "result": "Mock tool executed"}

class TestAgent(unittest.TestCase):
    """Test cases for GenAI Agent"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.config = {
            "services": {
                "redis": {
                    "host": "localhost",
                    "port": 6379
                },
                "llm": {
                    "type": "local",
                    "provider": "mock",
                    "model": "mock_model"
                }
            },
            "tools": {
                "enabled": ["mock_tool"]
            }
        }
        
        # Create patch for redis_bus
        self.redis_bus_patch = patch('genai_agent.agent.RedisMessageBus')
        self.mock_redis_bus = self.redis_bus_patch.start()
        self.mock_redis_bus_instance = MagicMock()
        self.mock_redis_bus.return_value = self.mock_redis_bus_instance
        
        # Create patch for llm_service
        self.llm_service_patch = patch('genai_agent.agent.LLMService')
        self.mock_llm_service = self.llm_service_patch.start()
        self.mock_llm_service_instance = MagicMock()
        self.mock_llm_service.return_value = self.mock_llm_service_instance
        
        # Create patch for memory_service
        self.memory_service_patch = patch('genai_agent.agent.MemoryService')
        self.mock_memory_service = self.memory_service_patch.start()
        self.mock_memory_service_instance = MagicMock()
        self.mock_memory_service.return_value = self.mock_memory_service_instance
        
        # Create patch for context_manager
        self.context_manager_patch = patch('genai_agent.agent.ContextManager')
        self.mock_context_manager = self.context_manager_patch.start()
        self.mock_context_manager_instance = MagicMock()
        self.mock_context_manager.return_value = self.mock_context_manager_instance
        
        # Create patch for task_manager
        self.task_manager_patch = patch('genai_agent.agent.TaskManager')
        self.mock_task_manager = self.task_manager_patch.start()
        self.mock_task_manager_instance = MagicMock()
        self.mock_task_manager.return_value = self.mock_task_manager_instance
        
        # Create patch for tool_registry
        self.tool_registry_patch = patch('genai_agent.agent.ToolRegistry')
        self.mock_tool_registry = self.tool_registry_patch.start()
        self.mock_tool_registry_instance = MagicMock()
        self.mock_tool_registry.return_value = self.mock_tool_registry_instance
    
    def tearDown(self):
        """Tear down test fixtures"""
        self.redis_bus_patch.stop()
        self.llm_service_patch.stop()
        self.memory_service_patch.stop()
        self.context_manager_patch.stop()
        self.task_manager_patch.stop()
        self.tool_registry_patch.stop()
    
    def test_init(self):
        """Test agent initialization"""
        agent = GenAIAgent(self.config)
        
        # Verify services are initialized
        self.mock_redis_bus.assert_called_once_with(self.config['services']['redis'])
        self.mock_llm_service.assert_called_once_with(self.config['services']['llm'])
        self.mock_memory_service.assert_called_once_with(self.mock_redis_bus_instance)
        
        # Verify core components are initialized
        self.mock_context_manager.assert_called_once_with(self.mock_memory_service_instance)
        self.mock_tool_registry.assert_called_once()
        self.mock_task_manager.assert_called_once_with(
            llm_service=self.mock_llm_service_instance,
            tool_registry=self.mock_tool_registry_instance,
            context_manager=self.mock_context_manager_instance
        )
    
    @patch('genai_agent.agent.__import__')
    def test_register_tools(self, mock_import):
        """Test tool registration"""
        # Mock the import function
        mock_module = MagicMock()
        mock_tool_class = MagicMock(return_value=MockTool())
        mock_module.MockTool = mock_tool_class
        mock_import.return_value = mock_module
        
        # Initialize agent
        agent = GenAIAgent(self.config)
        
        # Verify tool registry methods were called
        self.mock_tool_registry_instance.register_tool.assert_called()
    
    async def async_test_process_instruction(self):
        """Test processing an instruction"""
        # Setup mock returns
        self.mock_context_manager_instance.get_full_context.return_value = {}
        self.mock_task_manager_instance.plan_execution.return_value = MagicMock()
        self.mock_task_manager_instance.execute_plan.return_value = {
            "status": "success",
            "result": "Task executed"
        }
        
        # Initialize agent
        agent = GenAIAgent(self.config)
        
        # Process instruction
        result = await agent.process_instruction("Create a scene")
        
        # Verify methods were called
        self.mock_redis_bus_instance.start.assert_called_once()
        self.mock_context_manager_instance.get_full_context.assert_called_once()
        self.mock_task_manager_instance.plan_execution.assert_called_once_with(
            "Create a scene", {}
        )
        self.mock_task_manager_instance.execute_plan.assert_called_once()
        
        # Verify result
        self.assertEqual(result["status"], "success")
    
    async def async_test_cleanup(self):
        """Test cleanup method"""
        # Initialize agent
        agent = GenAIAgent(self.config)
        
        # Call cleanup
        await agent.cleanup()
        
        # Verify redis_bus.stop was called
        self.mock_redis_bus_instance.stop.assert_called_once()

def run_async_test(test_function):
    """Helper function to run async test methods"""
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test_function)

if __name__ == "__main__":
    unittest.main()
