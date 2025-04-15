"""
Task Manager for planning and executing tasks
"""

import logging
import json
from typing import Dict, Any, List, Optional

from genai_agent.services.llm import LLMService
from genai_agent.tools.registry import ToolRegistry
from genai_agent.core.context_manager import ContextManager

logger = logging.getLogger(__name__)

class Task:
    """
    Represents a single task to be executed
    """
    
    def __init__(self, tool_name: str, parameters: Dict[str, Any], description: str = ''):
        self.tool_name = tool_name
        self.parameters = parameters
        self.description = description

class ExecutionPlan:
    """
    Plan for executing a series of tasks
    """
    
    def __init__(self, tasks: List[Task], original_instruction: str):
        self.tasks = tasks
        self.original_instruction = original_instruction

class TaskManager:
    """
    Manages planning and execution of tasks
    """
    
    def __init__(self, llm_service: LLMService, tool_registry: ToolRegistry, 
                context_manager: ContextManager):
        """
        Initialize the Task Manager
        
        Args:
            llm_service: LLM service for task planning
            tool_registry: Tool registry for accessing tools
            context_manager: Context manager for maintaining state
        """
        self.llm_service = llm_service
        self.tool_registry = tool_registry
        self.context_manager = context_manager
        
        logger.info("Task Manager initialized")
    
    async def plan_execution(self, instruction: str, context: Optional[Dict[str, Any]] = None) -> ExecutionPlan:
        """
        Plan the execution of an instruction
        
        Args:
            instruction: User instruction to plan for
            context: Optional context information
            
        Returns:
            Execution plan with tasks
        """
        logger.info(f"Planning execution for: {instruction}")
        
        # Get available tools
        available_tools = self.tool_registry.list_tools()
        
        # Create prompt for task planning
        planning_prompt = f"""
        I need to break down the following instruction into a series of tasks that can be executed by available tools.
        
        Instruction: {instruction}
        
        Available tools: {', '.join(available_tools)}
        
        For each tool, here's what it can do:
        {self._get_tool_descriptions()}
        
        Please break down this instruction into a series of sequential tasks.
        For each task, specify:
        1. The tool to use (must be one of the available tools)
        2. The parameters to pass to the tool
        3. A brief description of what this task accomplishes
        
        Format your response as a JSON array of tasks, where each task has 'tool_name', 'parameters', and 'description' fields.
        """
        
        # Use LLM to generate plan
        plan_json = await self.llm_service.generate(planning_prompt, context)
        
        # Parse plan
        try:
            tasks_data = json.loads(plan_json)
            
            # Validate and create tasks
            tasks = []
            for task_data in tasks_data:
                tool_name = task_data.get('tool_name')
                parameters = task_data.get('parameters', {})
                description = task_data.get('description', '')
                
                # Ensure tool exists
                if tool_name not in available_tools:
                    logger.warning(f"Task references unknown tool: {tool_name}")
                    continue
                
                tasks.append(Task(tool_name, parameters, description))
            
            return ExecutionPlan(tasks, instruction)
            
        except Exception as e:
            logger.error(f"Error parsing task plan: {str(e)}")
            # Fallback to a simple plan
            default_tool = available_tools[0] if available_tools else "unknown_tool"
            return ExecutionPlan(
                [Task(default_tool, {'instruction': instruction}, 'Process the instruction')],
                instruction
            )
    
    async def execute_plan(self, plan: ExecutionPlan) -> Dict[str, Any]:
        """
        Execute a task plan
        
        Args:
            plan: Execution plan to execute
            
        Returns:
            Results of execution
        """
        logger.info(f"Executing plan with {len(plan.tasks)} tasks")
        
        results = []
        
        for i, task in enumerate(plan.tasks):
            logger.info(f"Executing task {i+1}/{len(plan.tasks)}: {task.description}")
            
            try:
                # Get tool
                tool = self.tool_registry.get_tool(task.tool_name)
                
                # Execute tool
                task_result = await tool.execute(task.parameters)
                
                # Store result
                results.append({
                    'task': task.description,
                    'tool': task.tool_name,
                    'status': 'success',
                    'result': task_result
                })
                
                # Update context with result
                await self.context_manager.update_context(f"task_{i+1}_result", task_result)
                
            except Exception as e:
                logger.error(f"Error executing task: {str(e)}")
                results.append({
                    'task': task.description,
                    'tool': task.tool_name,
                    'status': 'error',
                    'error': str(e)
                })
        
        # Combine results
        return {
            'instruction': plan.original_instruction,
            'tasks_executed': len(results),
            'tasks_succeeded': sum(1 for r in results if r['status'] == 'success'),
            'tasks_failed': sum(1 for r in results if r['status'] == 'error'),
            'results': results
        }
    
    def _get_tool_descriptions(self) -> str:
        """Get descriptions of all available tools"""
        descriptions = []
        
        for tool_name in self.tool_registry.list_tools():
            tool = self.tool_registry.get_tool(tool_name)
            descriptions.append(f"- {tool_name}: {tool.description}")
        
        return "\n".join(descriptions)
