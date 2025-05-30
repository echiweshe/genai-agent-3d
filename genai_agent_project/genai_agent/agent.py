"""
GenAI Agent - Main agent class
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Optional, Union

from genai_agent.services.llm import LLMService
from genai_agent.services.redis_bus import RedisMessageBus
from genai_agent.services.scene_manager import SceneManager
from genai_agent.tools.registry import ToolRegistry

from genai_agent.services.memory import MemoryService

logger = logging.getLogger(__name__)

class GenAIAgent:
    """
    GenAI Agent for 3D scene generation
    
    Central orchestration component that coordinates services and tools.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize GenAI Agent
        
        Args:
            config: Agent configuration
        """
        self.config = config
        
        # Initialize services
        self._init_services()
        
        # Register tools
        self._register_tools()
        
        logger.info("GenAI Agent initialized")
    
    def _init_services(self):
        """Initialize services"""
        # Redis Message Bus
        redis_config = self.config.get('redis', {})
        self.redis_bus = RedisMessageBus(redis_config)
        
        # LLM Service
        llm_config = self.config.get('llm', {})
        self.llm_service = LLMService()
        
        # Scene Manager
        scene_config = self.config.get('scene', {})
        self.scene_manager = SceneManager(self.redis_bus, scene_config)
        
        # Tool Registry
        self.tool_registry = ToolRegistry()
        
        # Store services for access by tools
        self.services = {
            'redis_bus': self.redis_bus,
            'llm_service': self.llm_service,
            'scene_manager': self.scene_manager,
            'tool_registry': self.tool_registry
        }
    
    def _register_tools(self):
        """Register tools"""
        # Get tool configurations
        tool_configs = self.config.get('tools', {})
        
        # Register each tool
        for tool_name, tool_config in tool_configs.items():
            self._register_tool(tool_name, tool_config)
    
    def _register_tool(self, tool_name: str, tool_config: Dict[str, Any]):
        """
        Register a tool
        
        Args:
            tool_name: Tool name
            tool_config: Tool configuration
        """
        try:
            module_path = tool_config.get('module')
            class_name = tool_config.get('class')
            
            if not module_path or not class_name:
                logger.warning(f"Invalid tool configuration for {tool_name}: missing module or class")
                return
            
            # Import tool class
            import importlib
            module = importlib.import_module(module_path, package=__package__)
            tool_class = getattr(module, class_name)
            
            # Create tool instance
            tool = tool_class(
                redis_bus=self.redis_bus,
                config=tool_config.get('config', {})
            )
            
            # Register tool
            self.tool_registry.register_tool(tool)
            
            logger.info(f"Registered tool: {tool_name}")
        except Exception as e:
            logger.error(f"Error registering tool {tool_name}: {str(e)}")
    
    async def process_instruction(self, instruction: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process a user instruction
        
        Args:
            instruction: User instruction
            context: Optional context information
            
        Returns:
            Processing result
        """
        logger.info(f"Processing instruction: {instruction}")
        
        try:
            # Connect to Redis
            await self.redis_bus.connect()
            
            # 1. Analyze instruction
            task = await self._analyze_instruction(instruction, context)
            
            # Handle situation where analysis failed or returned None
            if not task:
                # Use a default task focusing on scene generation since that's our specialty
                logger.warning("Task analysis failed, using default scene generation task")
                task = {
                    'task_type': 'scene_generation',
                    'description': instruction,
                    'parameters': {},
                    'instruction': instruction
                }
            
            # 2. Plan execution
            plan = await self._plan_execution(task)
            
            # Handle empty plans or planning failures
            if not plan or len(plan) == 0:
                logger.warning("Plan generation failed, using default plan")
                # Create a default plan with a scene generation step
                plan = [{
                    'tool_name': 'scene_generator',
                    'parameters': {
                        'description': instruction,
                        'style': 'realistic'
                    },
                    'description': f"Generate a scene based on the description: {instruction}"
                }]
            
            # 3. Execute plan
            result = await self._execute_plan(plan)
            
            return result
        except Exception as e:
            logger.error(f"Error processing instruction: {str(e)}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _analyze_instruction(self, instruction: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Analyze a user instruction
        
        Args:
            instruction: User instruction
            context: Optional context information
            
        Returns:
            Structured task
        """
        logger.info("Analyzing instruction")
        
        try:
            # Use LLM to classify the instruction
            task = await self.llm_service.classify_task(instruction)
            
            # Add original instruction
            if task:
                task['instruction'] = instruction
                
                # Add context if provided
                if context:
                    task['context'] = context
                
                logger.info(f"Analyzed task: {task.get('task_type')}")
            else:
                logger.warning("Task analysis returned None")
                
            return task
        except Exception as e:
            logger.error(f"Error analyzing instruction: {str(e)}")
            return None
    
    async def _plan_execution(self, task: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Plan execution steps
        
        Args:
            task: Structured task
            
        Returns:
            Execution plan (list of steps)
        """
        logger.info(f"Planning execution for task: {task.get('task_type')}")
        
        try:
            # Get available tools
            available_tools = self.tool_registry.get_tool_info()
            
            # Use LLM to plan execution
            plan = await self.llm_service.plan_task_execution(task, available_tools)
            
            if plan:
                logger.info(f"Generated execution plan with {len(plan)} steps")
            else:
                logger.warning("Plan generation returned None or empty plan")
                
            return plan
        except Exception as e:
            logger.error(f"Error planning execution: {str(e)}")
            return []
    
    async def _execute_plan(self, plan: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute a plan
        
        Args:
            plan: Execution plan (list of steps)
            
        Returns:
            Execution result
        """
        logger.info(f"Executing plan with {len(plan)} steps")
        
        results = []
        
        for i, step in enumerate(plan):
            logger.info(f"Executing step {i+1}: {step.get('description', 'Unnamed step')}")
            
            # Get tool name and parameters
            tool_name = step.get('tool_name')
            parameters = step.get('parameters', {})
            
            try:
                # Execute tool
                step_result = await self.tool_registry.execute_tool(tool_name, parameters)
                
                # Store result
                results.append({
                    'step': i + 1,
                    'description': step.get('description', 'Unnamed step'),
                    'tool': tool_name,
                    'result': step_result
                })
                
                logger.info(f"Step {i+1} completed")
            except Exception as e:
                logger.error(f"Error executing step {i+1}: {str(e)}")
                
                # Store error
                results.append({
                    'step': i + 1,
                    'description': step.get('description', 'Unnamed step'),
                    'tool': tool_name,
                    'result': {
                        'status': 'error',
                        'error': str(e)
                    }
                })
        
        # Look for any successful steps in the results
        any_success = any(
            result.get('result', {}).get('status') == 'success'
            for result in results
        )
        
        # Process results
        return {
            'status': 'success' if any_success else 'error',
            'steps_executed': len(results),
            'results': results
        }
    
    async def close(self):
        """Close agent and release resources"""
        # Disconnect from Redis
        await self.redis_bus.disconnect()
        
        logger.info("Agent closed")
