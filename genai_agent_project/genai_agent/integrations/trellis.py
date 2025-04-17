"""
Integration with Microsoft TRELLIS (https://github.com/microsoft/TRELLIS)

This integration enables advanced reasoning and planning capabilities for the GenAI Agent.
"""

import os
import sys
import logging
import json
import importlib.util
import tempfile
import asyncio
from typing import Dict, Any, List, Optional, Tuple

from genai_agent.integrations.base import BaseIntegration

logger = logging.getLogger(__name__)

class TrellisIntegration(BaseIntegration):
    """Integration with Microsoft TRELLIS"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the TRELLIS integration
        
        Args:
            config: Integration configuration
                - trellis_path: Path to TRELLIS installation
                - api_key: API key for language models (if needed)
                - model: Language model to use (default: gpt-4)
                - reasoning_examples_path: Path to reasoning examples
        """
        super().__init__(config)
    
    def _initialize(self):
        """Initialize the TRELLIS integration and check if it's available"""
        self.trellis_path = self.config.get('trellis_path')
        
        if not self.trellis_path:
            raise ValueError("TRELLIS path is required")
        
        if not os.path.exists(self.trellis_path):
            raise FileNotFoundError(f"TRELLIS not found at {self.trellis_path}")
        
        # Add TRELLIS path to Python path
        sys.path.append(self.trellis_path)
        
        # Try to import TRELLIS modules
        try:
            spec = importlib.util.find_spec("trellis")
            if spec is None:
                raise ImportError("TRELLIS module not found")
        except ImportError as e:
            raise ImportError(f"Failed to import TRELLIS: {str(e)}")
        
        # Configure TRELLIS
        self.api_key = self.config.get('api_key')
        self.model = self.config.get('model', 'gpt-4')
        self.reasoning_examples_path = self.config.get('reasoning_examples_path')
        
        if self.reasoning_examples_path and not os.path.exists(self.reasoning_examples_path):
            logger.warning(f"Reasoning examples not found at {self.reasoning_examples_path}")
        
        # Try to get the version
        try:
            # Look for version in package
            try:
                import trellis
                self._version = getattr(trellis, "__version__", "Unknown")
            except (ImportError, AttributeError):
                # Try to get version from setup.py or pyproject.toml
                setup_py = os.path.join(self.trellis_path, 'setup.py')
                if os.path.exists(setup_py):
                    with open(setup_py, 'r') as f:
                        content = f.read()
                        import re
                        version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                        if version_match:
                            self._version = version_match.group(1)
                        else:
                            self._version = "Unknown"
                else:
                    self._version = "Unknown"
        except Exception as e:
            logger.warning(f"Failed to read TRELLIS version: {str(e)}")
            self._version = "Unknown"
        
        # Dynamic import (will be done as needed to avoid import errors at initialization)
        self.trellis_module = None
        self.agent_module = None
        self.reasoner_module = None
    
    def _lazy_import(self):
        """Lazily import TRELLIS modules when needed"""
        if self.trellis_module is None:
            try:
                import trellis
                self.trellis_module = trellis
                
                from trellis.agent import Agent
                self.agent_module = Agent
                
                from trellis.reasoner import Reasoner
                self.reasoner_module = Reasoner
            except ImportError as e:
                logger.error(f"Failed to import TRELLIS modules: {str(e)}")
                raise ImportError(f"Failed to import TRELLIS modules: {str(e)}")
    
    def get_capabilities(self) -> List[str]:
        """Get the list of capabilities provided by TRELLIS"""
        return [
            'multi_step_reasoning',
            'complex_planning',
            'knowledge_graph_reasoning',
            'step_by_step_execution',
            'spatial_reasoning'
        ]
    
    async def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an operation using TRELLIS
        
        Args:
            operation: Operation to execute
                - reason: Perform step-by-step reasoning
                - plan: Generate a complex plan
                - execute_plan: Execute a plan with feedback
                - knowledge_graph: Generate a knowledge graph
            parameters: Operation parameters
                
        Returns:
            Operation result
        """
        if not self.is_available:
            return {
                'status': 'error',
                'error': 'TRELLIS integration is not available'
            }
        
        try:
            # Lazily import TRELLIS modules
            self._lazy_import()
            
            if operation == 'reason':
                return await self._reason(parameters)
            elif operation == 'plan':
                return await self._plan(parameters)
            elif operation == 'execute_plan':
                return await self._execute_plan(parameters)
            elif operation == 'knowledge_graph':
                return await self._knowledge_graph(parameters)
            else:
                return {
                    'status': 'error',
                    'error': f"Unsupported operation: {operation}"
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _reason(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform step-by-step reasoning
        
        Args:
            parameters:
                - query: Question or problem to reason about
                - context: Additional context (optional)
                - model: Language model to use (optional)
                - max_steps: Maximum reasoning steps (optional)
                
        Returns:
            Reasoning result
        """
        query = parameters.get('query')
        if not query:
            return {
                'status': 'error',
                'error': 'No query provided'
            }
        
        context = parameters.get('context', '')
        model = parameters.get('model', self.model)
        max_steps = parameters.get('max_steps', 5)
        
        # Run reasoning in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._run_reasoning,
            query,
            context,
            model,
            max_steps
        )
        
        return result
    
    def _run_reasoning(self, query: str, context: str, model: str, max_steps: int) -> Dict[str, Any]:
        """
        Run TRELLIS reasoning process
        
        This runs in a separate thread via run_in_executor
        """
        try:
            # Initialize the reasoner
            reasoner = self.reasoner_module(
                model=model,
                api_key=self.api_key,
                max_steps=max_steps
            )
            
            # Run reasoning
            reasoning_result = reasoner.reason(
                query=query,
                context=context
            )
            
            # Extract the results
            steps = reasoning_result.steps
            conclusion = reasoning_result.conclusion
            
            return {
                'status': 'success',
                'query': query,
                'steps': [step.to_dict() for step in steps],
                'conclusion': conclusion,
                'step_count': len(steps)
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _plan(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complex plan
        
        Args:
            parameters:
                - goal: Goal to achieve
                - constraints: Constraints to consider (optional)
                - resources: Available resources (optional)
                - model: Language model to use (optional)
                - max_depth: Maximum plan depth (optional)
                
        Returns:
            Planning result
        """
        goal = parameters.get('goal')
        if not goal:
            return {
                'status': 'error',
                'error': 'No goal provided'
            }
        
        constraints = parameters.get('constraints', [])
        resources = parameters.get('resources', [])
        model = parameters.get('model', self.model)
        max_depth = parameters.get('max_depth', 3)
        
        # Run planning in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._run_planning,
            goal,
            constraints,
            resources,
            model,
            max_depth
        )
        
        return result
    
    def _run_planning(self, goal: str, constraints: List[str], resources: List[str], 
                      model: str, max_depth: int) -> Dict[str, Any]:
        """
        Run TRELLIS planning process
        
        This runs in a separate thread via run_in_executor
        """
        try:
            # Initialize the agent with planning capabilities
            agent = self.agent_module(
                model=model,
                api_key=self.api_key
            )
            
            # Format the planning request
            planning_request = {
                'goal': goal,
                'constraints': constraints,
                'resources': resources,
                'max_depth': max_depth
            }
            
            # Run planning
            plan_result = agent.plan(**planning_request)
            
            # Extract the results
            steps = plan_result.steps
            explanation = plan_result.explanation
            
            return {
                'status': 'success',
                'goal': goal,
                'plan': [step.to_dict() for step in steps],
                'explanation': explanation,
                'step_count': len(steps)
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _execute_plan(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a plan with feedback
        
        Args:
            parameters:
                - plan: Plan to execute (list of steps)
                - tools: Tools available for execution (optional)
                - model: Language model to use (optional)
                - max_iterations: Maximum execution iterations (optional)
                
        Returns:
            Execution result
        """
        plan = parameters.get('plan')
        if not plan:
            return {
                'status': 'error',
                'error': 'No plan provided'
            }
        
        tools = parameters.get('tools', {})
        model = parameters.get('model', self.model)
        max_iterations = parameters.get('max_iterations', 10)
        
        # Run plan execution in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._run_execution,
            plan,
            tools,
            model,
            max_iterations
        )
        
        return result
    
    def _run_execution(self, plan: List[Dict[str, Any]], tools: Dict[str, Any], 
                       model: str, max_iterations: int) -> Dict[str, Any]:
        """
        Run TRELLIS plan execution process
        
        This runs in a separate thread via run_in_executor
        """
        try:
            # Initialize the agent with execution capabilities
            agent = self.agent_module(
                model=model,
                api_key=self.api_key,
                tools=tools
            )
            
            # Format the plan for execution
            steps = []
            for step_data in plan:
                step = self.trellis_module.plan.PlanStep(
                    description=step_data.get('description', ''),
                    tool=step_data.get('tool'),
                    parameters=step_data.get('parameters', {})
                )
                steps.append(step)
            
            execution_plan = self.trellis_module.plan.Plan(steps=steps)
            
            # Execute the plan
            execution_result = agent.execute_plan(
                plan=execution_plan,
                max_iterations=max_iterations
            )
            
            # Extract the results
            executed_steps = execution_result.steps
            success = execution_result.success
            
            return {
                'status': 'success',
                'executed_steps': [step.to_dict() for step in executed_steps],
                'success': success,
                'step_count': len(executed_steps)
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    async def _knowledge_graph(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a knowledge graph
        
        Args:
            parameters:
                - topic: Topic for the knowledge graph
                - context: Additional context (optional)
                - model: Language model to use (optional)
                - max_nodes: Maximum number of nodes (optional)
                
        Returns:
            Knowledge graph result
        """
        topic = parameters.get('topic')
        if not topic:
            return {
                'status': 'error',
                'error': 'No topic provided'
            }
        
        context = parameters.get('context', '')
        model = parameters.get('model', self.model)
        max_nodes = parameters.get('max_nodes', 20)
        
        # Run knowledge graph generation in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            self._run_knowledge_graph,
            topic,
            context,
            model,
            max_nodes
        )
        
        return result
    
    def _run_knowledge_graph(self, topic: str, context: str, model: str, max_nodes: int) -> Dict[str, Any]:
        """
        Run TRELLIS knowledge graph generation process
        
        This runs in a separate thread via run_in_executor
        """
        try:
            # Initialize the knowledge graph generator
            from trellis.knowledge import KnowledgeGraphGenerator
            kg_generator = KnowledgeGraphGenerator(
                model=model,
                api_key=self.api_key
            )
            
            # Generate the knowledge graph
            kg_result = kg_generator.generate(
                topic=topic,
                context=context,
                max_nodes=max_nodes
            )
            
            # Extract the results
            nodes = kg_result.nodes
            edges = kg_result.edges
            
            return {
                'status': 'success',
                'topic': topic,
                'nodes': [node.to_dict() for node in nodes],
                'edges': [edge.to_dict() for edge in edges],
                'node_count': len(nodes),
                'edge_count': len(edges)
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
