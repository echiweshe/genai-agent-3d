#!/usr/bin/env python3
"""
Restart Services with Claude as Default Provider

This script sets Claude as the default LLM provider and restarts the services
for the GenAI Agent 3D project.
"""

import os
import sys
import subprocess
import time
import signal
import psutil
from pathlib import Path
import logging
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def set_claude_default(project_root):
    """Set Claude as the default LLM provider"""
    logger.info("Setting Claude as the default LLM provider...")
    
    # Update .env file
    env_path = project_root / "genai_agent_project" / ".env"
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Update LLM settings
        content = content.replace('LLM_PROVIDER=ollama', 'LLM_PROVIDER=anthropic')
        content = content.replace('LLM_TYPE=local', 'LLM_TYPE=cloud')
        
        # Make sure we have an appropriate Claude model
        if 'LLM_MODEL=claude' not in content:
            content = content.replace('LLM_MODEL=llama3', 'LLM_MODEL=claude-3-sonnet-20240229')
        
        # Write updated content
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        logger.info(f"Updated .env file: {env_path}")
    else:
        logger.warning(f".env file not found: {env_path}")
    
    # Update config.yaml file if it exists
    config_path = project_root / "genai_agent_project" / "config.yaml"
    if config_path.exists():
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Update LLM settings
            if 'llm' not in config:
                config['llm'] = {}
            
            config['llm']['provider'] = 'anthropic'
            config['llm']['model'] = 'claude-3-sonnet-20240229'
            config['llm']['type'] = 'cloud'
            
            # Write updated config
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False)
            
            logger.info(f"Updated config.yaml file: {config_path}")
        except Exception as e:
            logger.error(f"Error updating config.yaml: {str(e)}")
    else:
        logger.warning(f"config.yaml file not found: {config_path}")

def find_services_to_restart(project_root):
    """Find services that need to be restarted"""
    # This is a simplified approach - in a real project you might have a more
    # sophisticated way to track running services
    services = []
    
    # Check if the service manager script exists
    service_manager_path = project_root / "genai_agent_project" / "manage_services.py"
    if service_manager_path.exists():
        services.append(('manage_services.py', ['restart', 'all']))
    
    # Check for other service scripts
    backend_service_path = project_root / "genai_agent_project" / "web" / "backend" / "main.py"
    if backend_service_path.exists():
        services.append(('web/backend/main.py', []))
    
    return services

def kill_existing_processes():
    """Kill existing Python processes related to the project"""
    logger.info("Stopping existing processes...")
    
    # Get the name of the script that's checking
    current_script = Path(sys.argv[0]).name
    
    # Look for Python processes running relevant scripts
    process_names = ['manage_services.py', 'main.py', 'run_llm_worker.py']
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Skip the current process
            if proc.pid == os.getpid():
                continue
            
            # Check if this is a Python process
            if proc.name() in ['python', 'python.exe', 'python3', 'python3.exe']:
                cmdline = proc.cmdline()
                
                # Check if it's running one of our target scripts
                if any(script in ' '.join(cmdline) for script in process_names):
                    logger.info(f"Terminating process {proc.pid}: {' '.join(cmdline)}")
                    try:
                        proc.terminate()
                        proc.wait(timeout=5)
                    except psutil.TimeoutExpired:
                        logger.warning(f"Process {proc.pid} did not terminate gracefully, killing...")
                        proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

def restart_services(project_root):
    """Restart services with updated settings"""
    logger.info("Restarting services...")
    
    # Kill existing processes
    kill_existing_processes()
    
    # Allow time for processes to stop
    time.sleep(2)
    
    # Find services to restart
    services = find_services_to_restart(project_root)
    
    if not services:
        logger.warning("No services found to restart")
        logger.info("You may need to manually restart the services")
        return
    
    # Restart each service
    for script, args in services:
        script_path = project_root / "genai_agent_project" / script
        if script_path.exists():
            try:
                # Build command
                cmd = [sys.executable, str(script_path)] + args
                
                logger.info(f"Starting service: {script}")
                
                # Start the process and detach
                if os.name == 'nt':  # Windows
                    process = subprocess.Popen(
                        cmd,
                        creationflags=subprocess.CREATE_NEW_CONSOLE,
                        cwd=str(project_root)
                    )
                else:  # Unix
                    process = subprocess.Popen(
                        cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        preexec_fn=os.setsid,
                        cwd=str(project_root)
                    )
                
                logger.info(f"Started process with PID {process.pid}")
            except Exception as e:
                logger.error(f"Error starting service {script}: {str(e)}")
        else:
            logger.warning(f"Service script not found: {script_path}")

def main():
    """Main function"""
    # Get project root
    project_root = Path(__file__).parent.absolute()
    
    print("===========================================")
    print("  Restart with Claude - GenAI Agent 3D")
    print("===========================================")
    print("This script will:")
    print("1. Set Claude as the default LLM provider")
    print("2. Restart all services")
    print("===========================================")
    
    # Set Claude as default
    set_claude_default(project_root)
    
    # Restart services
    restart_services(project_root)
    
    print("\n✅ Services have been restarted with Claude as the default provider")
    print("You can now use Claude for all LLM operations in GenAI Agent 3D")
    
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
