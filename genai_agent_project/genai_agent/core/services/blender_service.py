"""
Blender Service Module
-------------------
Provides robust execution of Blender scripts with proper path resolution
for different operating systems and operation modes.
"""

import os
import sys
import json
import time
import logging
import platform
import subprocess
import tempfile
from typing import Dict, Any, Optional, List, Union
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("BlenderService")

class BlenderService:
    """Service for reliable execution of Blender operations."""
    
    def __init__(self):
        """Initialize the Blender service with configuration from the service registry."""
        from genai_agent.core.services.service_initialization import get_registry
        
        self.registry = get_registry()
        self.config = self.registry.config
        
        # Get Blender executable path from config
        self.blender_path = self._resolve_blender_path()
        
        # Blender script directory
        self.scripts_dir = self._resolve_scripts_dir()
        
        # Output directory from registry
        self.output_dir = self.registry.get_output_directory()
        
        # Execution settings
        self.headless = self.config.get("BLENDER_HEADLESS", "True").lower() in ("true", "1", "yes")
        self.timeout = float(self.config.get("BLENDER_TIMEOUT", 300.0))  # 5 minutes default
        
        logger.info(f"Blender Service initialized with path: {self.blender_path}")
        logger.info(f"Using scripts directory: {self.scripts_dir}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Running in {'headless' if self.headless else 'UI'} mode")
    
    def _resolve_blender_path(self) -> str:
        """Resolve the path to the Blender executable for the current OS."""
        # First check if explicitly set in config
        blender_path = self.config.get("BLENDER_PATH")
        if blender_path and os.path.exists(blender_path):
            return blender_path
        
        # Otherwise determine based on platform
        system = platform.system()
        
        if system == "Windows":
            # Check common installation paths on Windows
            common_paths = [
                r"C:\Program Files\Blender Foundation\Blender 4.0\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender 3.6\blender.exe",
                r"C:\Program Files\Blender Foundation\Blender\blender.exe",
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    return path
            
            # Check if in the system path
            try:
                from shutil import which
                blender_path = which("blender")
                if blender_path:
                    return blender_path
            except Exception:
                pass
            
        elif system == "Darwin":  # macOS
            # Check common installation paths on macOS
            common_paths = [
                "/Applications/Blender.app/Contents/MacOS/Blender",
                "/Applications/Blender/Blender.app/Contents/MacOS/Blender",
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    return path
                
        elif system == "Linux":
            # Check if in the system path on Linux
            try:
                from shutil import which
                blender_path = which("blender")
                if blender_path:
                    return blender_path
            except Exception:
                pass
            
            # Check common installation paths on Linux
            common_paths = [
                "/usr/bin/blender",
                "/usr/local/bin/blender",
                "/snap/bin/blender",
                "/opt/blender/blender",
            ]
            
            for path in common_paths:
                if os.path.exists(path):
                    return path
        
        # If we couldn't find Blender, raise error
        raise FileNotFoundError(
            "Could not find Blender executable. Please set BLENDER_PATH in your config."
        )
    
    def _resolve_scripts_dir(self) -> str:
        """Resolve the path to the Blender scripts directory."""
        # First check if explicitly set in config
        scripts_dir = self.config.get("BLENDER_SCRIPTS_DIR")
        if scripts_dir and os.path.exists(scripts_dir):
            return scripts_dir
        
        # Otherwise, look in standard locations
        project_root = self.registry.project_root
        
        # Try to find tools/blender_scripts or similar
        potential_paths = [
            project_root / "genai_agent" / "tools" / "blender",
            project_root / "tools" / "blender_scripts",
            project_root / "genai_agent" / "tools" / "blender_scripts",
            project_root / "blender_scripts",
        ]
        
        for path in potential_paths:
            if path.exists() and path.is_dir():
                return str(path)
        
        # If we couldn't find the scripts directory, create it
        scripts_dir = project_root / "genai_agent" / "tools" / "blender_scripts"
        os.makedirs(scripts_dir, exist_ok=True)
        
        logger.warning(f"Created new scripts directory at: {scripts_dir}")
        return str(scripts_dir)
    
    def run_script(self, 
                  script_path: str, 
                  params: Optional[Dict[str, Any]] = None,
                  output_file: Optional[str] = None,
                  timeout: Optional[float] = None,
                  headless: Optional[bool] = None) -> Dict[str, Any]:
        """
        Run a Blender Python script with parameters.
        
        Args:
            script_path: Path to the Blender Python script
            params: Dictionary of parameters to pass to the script
            output_file: If specified, save output to this file
            timeout: Override the default timeout
            headless: Override the default headless mode
            
        Returns:
            Dictionary with execution results
        """
        # Resolve script path
        script_path = self._resolve_script_path(script_path)
        
        # Set execution mode
        headless = self.headless if headless is None else headless
        timeout = self.timeout if timeout is None else timeout
        
        # Create temporary JSON file for parameters
        params_file = None
        if params:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w') as f:
                json.dump(params, f)
                params_file = f.name
        
        # Prepare command
        cmd = [self.blender_path]
        
        # Add headless mode if needed
        if headless:
            cmd.extend(["--background", "--python"])
        else:
            cmd.extend(["--python"])
        
        cmd.append(script_path)
        
        # Add parameters file path if needed
        if params_file:
            cmd.extend(["--", params_file])
            
            # Add output path if specified
            if output_file:
                if not os.path.isabs(output_file):
                    output_file = os.path.join(self.output_dir, output_file)
                cmd.append(output_file)
        
        logger.info(f"Executing Blender script: {script_path}")
        logger.info(f"Command: {' '.join(cmd)}")
        
        # Run the command
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )
            
            # Check for errors
            if result.returncode != 0:
                logger.error(f"Blender script execution failed with code {result.returncode}")
                logger.error(f"STDERR: {result.stderr}")
                
                return {
                    "success": False,
                    "error": result.stderr,
                    "returncode": result.returncode,
                    "output": result.stdout
                }
            
            # Success
            logger.info(f"Blender script executed successfully")
            
            return {
                "success": True,
                "output": result.stdout,
                "error": result.stderr,
                "returncode": result.returncode,
                "output_file": output_file if output_file else None
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"Blender script execution timed out after {timeout} seconds")
            return {
                "success": False,
                "error": f"Execution timed out after {timeout} seconds",
                "returncode": -1,
                "output": ""
            }
            
        except Exception as e:
            logger.error(f"Error executing Blender script: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "returncode": -1,
                "output": ""
            }
            
        finally:
            # Clean up temporary parameter file
            if params_file and os.path.exists(params_file):
                try:
                    os.unlink(params_file)
                except Exception as e:
                    logger.warning(f"Failed to remove temporary file {params_file}: {str(e)}")
    
    def _resolve_script_path(self, script_path: str) -> str:
        """Resolve the full path to a Blender script."""
        if os.path.isabs(script_path) and os.path.exists(script_path):
            return script_path
        
        # Check relative to scripts directory
        full_path = os.path.join(self.scripts_dir, script_path)
        if os.path.exists(full_path):
            return full_path
        
        # Try adding .py extension if not present
        if not script_path.endswith('.py'):
            full_path_with_ext = f"{full_path}.py"
            if os.path.exists(full_path_with_ext):
                return full_path_with_ext
        
        # If not found, raise error
        raise FileNotFoundError(f"Blender script not found: {script_path}")
    
    async def run_script_async(self, 
                              script_path: str, 
                              params: Optional[Dict[str, Any]] = None,
                              output_file: Optional[str] = None,
                              timeout: Optional[float] = None,
                              headless: Optional[bool] = None) -> Dict[str, Any]:
        """
        Run a Blender Python script asynchronously with parameters.
        
        Args:
            script_path: Path to the Blender Python script
            params: Dictionary of parameters to pass to the script
            output_file: If specified, save output to this file
            timeout: Override the default timeout
            headless: Override the default headless mode
            
        Returns:
            Dictionary with execution results
        """
        import asyncio
        
        # Create a copy of the function to run in a thread
        def run_script_thread():
            return self.run_script(
                script_path=script_path,
                params=params,
                output_file=output_file,
                timeout=timeout,
                headless=headless
            )
        
        # Run the blocking function in a thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_script_thread)
        
        return result
    
    def generate_model(self, 
                      description: str, 
                      output_file: str = 'model.glb',
                      model_type: str = 'basic',
                      **kwargs) -> Dict[str, Any]:
        """
        Generate a 3D model based on a description.
        
        Args:
            description: Text description of the model to generate
            output_file: Name of the output file
            model_type: Type of model to generate (basic, detailed, etc.)
            **kwargs: Additional parameters for model generation
            
        Returns:
            Dictionary with generation results
        """
        # Prepare parameters for the model generation script
        params = {
            "description": description,
            "model_type": model_type,
            **kwargs
        }
        
        # Determine which script to use based on model type
        script_name = f"generate_{model_type}_model.py"
        
        # Run the script
        result = self.run_script(
            script_path=script_name,
            params=params,
            output_file=output_file
        )
        
        return result
    
    def convert_model(self, 
                     input_file: str, 
                     output_format: str = 'glb',
                     output_file: Optional[str] = None,
                     **kwargs) -> Dict[str, Any]:
        """
        Convert a 3D model from one format to another.
        
        Args:
            input_file: Path to the input model file
            output_format: Format to convert to (glb, obj, etc.)
            output_file: Name of the output file, will auto-generate if None
            **kwargs: Additional parameters for conversion
            
        Returns:
            Dictionary with conversion results
        """
        # Generate output filename if not provided
        if not output_file:
            input_name = os.path.splitext(os.path.basename(input_file))[0]
            output_file = f"{input_name}.{output_format}"
        
        # Prepare parameters for the conversion script
        params = {
            "input_file": input_file,
            "output_format": output_format,
            **kwargs
        }
        
        # Run the conversion script
        result = self.run_script(
            script_path="convert_model.py",
            params=params,
            output_file=output_file
        )
        
        return result
