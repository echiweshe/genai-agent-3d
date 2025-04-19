#!/usr/bin/env python
"""
Service Manager for GenAI Agent 3D
This script manages (starts, stops, restarts) all required services for the GenAI Agent 3D platform.
"""
import os
import sys
import subprocess
import platform
import time
import socket
import signal
try:
    import psutil
except ImportError:
    print("psutil not installed. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil"])
    import psutil
import argparse
import requests
from urllib.parse import urljoin
import json

# Configuration
CONFIG = {
    "redis": {
        "port": 6379,
        "command": "redis-server",
        "windows_command": "redis-server",
        "unix_command": "redis-server",
        "health_check": lambda: check_redis_health(),
        "process_name": "redis-server"
    },
    "ollama": {
        "port": 11434,
        "command": "ollama serve",
        "windows_command": "ollama serve",
        "unix_command": "ollama serve",
        "health_check": lambda: check_ollama_health(),
        "process_name": "ollama"
    },
    "backend": {
        "port": 8000,
        "command": "{python} run_server.py",
        "windows_command": "{python} run_server.py",
        "unix_command": "{python} run_server.py",
        "health_check": lambda: check_backend_health(),
        "process_name": "run_server.py",
        "working_dir": "web/backend"
    },
    "frontend": {
        "port": 3000,
        "command": "{npm} start",
        "windows_command": "{npm_cmd} start",
        "unix_command": "{npm} start",
        "health_check": lambda: check_frontend_health(),
        "process_name": "node",
        "working_dir": "web/frontend"
    }
}

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_colored(text, color):
    """Print colored text"""
    color_code = getattr(Colors, color.upper(), Colors.ENDC)
    print(f"{color_code}{text}{Colors.ENDC}")

def check_port(host, port):
    """Check if a port is open on the specified host"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(1)
        try:
            s.connect((host, port))
            return True
        except:
            return False

def check_redis_health():
    """Check if Redis is healthy"""
    try:
        result = subprocess.run(
            ["redis-cli", "ping"],
            capture_output=True,
            text=True,
            timeout=5
        )
        return "PONG" in result.stdout
    except:
        return False

def check_ollama_health():
    """Check if Ollama is healthy"""
    try:
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_backend_health():
    """Check if backend API is healthy"""
    try:
        response = requests.get("http://localhost:8000/api/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def check_frontend_health():
    """Check if frontend is healthy"""
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_process_by_name_and_port(name, port=None):
    """Find a process by name and optionally port"""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if the process name matches
            proc_name = proc.info['name'].lower()
            proc_cmdline = ' '.join(proc.info['cmdline']).lower() if proc.info['cmdline'] else ''
            
            if (name.lower() in proc_name or name.lower() in proc_cmdline):
                # If port is specified, we'll check it separately
                # This is more compatible with different versions of psutil
                processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return processes

def kill_process(proc, force=False):
    """Kill a process"""
    try:
        if platform.system() == "Windows":
            if force:
                proc.kill()
            else:
                proc.terminate()
        else:
            if force:
                os.kill(proc.pid, signal.SIGKILL)
            else:
                os.kill(proc.pid, signal.SIGTERM)
        return True
    except Exception as e:
        print(f"Error killing process {proc.pid}: {e}")
        return False

def kill_processes_by_port(port):
    """Kill all processes using a specific port"""
    killed = False
    
    if platform.system() == "Windows":
        try:
            # On Windows, use netstat to find the process ID
            result = subprocess.run(
                f"netstat -ano | findstr :{port}",
                capture_output=True,
                text=True,
                shell=True
            )
            
            for line in result.stdout.splitlines():
                if "LISTENING" in line:
                    parts = line.strip().split()
                    pid = parts[-1]
                    try:
                        subprocess.run(f"taskkill /F /PID {pid}", check=False, shell=True)
                        print(f"Killed process with PID: {pid} using port {port}")
                        killed = True
                    except:
                        pass
        except:
            pass
    else:
        try:
            # On Unix systems, use lsof to find the process ID
            result = subprocess.run(
                ["lsof", "-i", f":{port}", "-t"],
                capture_output=True,
                text=True
            )
            
            for pid in result.stdout.splitlines():
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    print(f"Killed process with PID: {pid} using port {port}")
                    killed = True
                except:
                    pass
        except:
            pass
    
    return killed

def start_service(service_name, force_restart=False):
    """Start a service if it's not already running"""
    service = CONFIG.get(service_name)
    if not service:
        print_colored(f"Unknown service: {service_name}", "red")
        return False
    
    print_colored(f"Managing {service_name} service...", "blue")
    
    # Check if the service is already running (port check)
    port_in_use = check_port("localhost", service["port"])
    health_ok = service["health_check"]()
    
    if port_in_use and health_ok and not force_restart:
        print_colored(f"✅ {service_name} is already running on port {service['port']} and healthy", "green")
        return True
    
    # If we need to restart but the port is in use, kill the existing process
    if (port_in_use and not health_ok) or force_restart:
        print_colored(f"⚠️ {service_name} is running but {'unhealthy' if not health_ok else 'restart requested'}", "yellow")
        
        # Find processes by name or by port
        processes = get_process_by_name_and_port(service["process_name"], service["port"])
        
        if processes:
            print_colored(f"Found {len(processes)} {service_name} processes to terminate", "yellow")
            for proc in processes:
                kill_process(proc)
                print_colored(f"✅ Terminated {service_name} process with PID: {proc.pid}", "green")
        else:
            # If process not found by name, kill by port
            print_colored(f"No {service_name} processes found by name, killing processes by port {service['port']}", "yellow")
            kill_processes_by_port(service["port"])
        
        # Wait for port to be released
        for _ in range(5):
            if not check_port("localhost", service["port"]):
                break
            time.sleep(1)
        
        if check_port("localhost", service["port"]):
            print_colored(f"⚠️ Port {service['port']} is still in use after killing processes", "red")
            return False
    
    # Start the service
    print_colored(f"Starting {service_name} service...", "blue")
    
    # Get project directory
    project_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Get working directory
    working_dir = project_dir
    if "working_dir" in service:
        working_dir = os.path.join(project_dir, service["working_dir"])
    
    if not os.path.exists(working_dir):
        print_colored(f"❌ Working directory not found: {working_dir}", "red")
        return False
    
    # Determine command
    cmd = service["command"]
    if platform.system() == "Windows":
        cmd = service["windows_command"]
    else:
        cmd = service["unix_command"]
    
    # Replace variables in command
    cmd = cmd.replace("{python}", sys.executable)
    cmd = cmd.replace("{npm}", "npm")
    cmd = cmd.replace("{npm_cmd}", "npm.cmd" if platform.system() == "Windows" else "npm")
    
    # Start the service
    try:
        if platform.system() == "Windows":
            process = subprocess.Popen(
                cmd,
                cwd=working_dir,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
                shell=True
            )
        else:
            process = subprocess.Popen(
                cmd,
                cwd=working_dir,
                start_new_session=True,
                shell=True
            )
        
        # Wait for service to start
        print_colored(f"Waiting for {service_name} to start...", "blue")
        max_wait = 30
        for i in range(max_wait):
            if check_port("localhost", service["port"]):
                time.sleep(2)  # Give additional time for the service to initialize fully
                if service["health_check"]():
                    print_colored(f"✅ {service_name} started successfully and is healthy", "green")
                    return True
                else:
                    print_colored(f"🔄 {service_name} started but health check failed, retrying... ({i+1}/{max_wait})", "yellow")
            
            if i < max_wait - 1:  # Don't sleep on the last iteration
                time.sleep(1)
        
        print_colored(f"❌ {service_name} failed to start or become healthy", "red")
        return False
    
    except Exception as e:
        print_colored(f"❌ Error starting {service_name}: {e}", "red")
        return False

def stop_service(service_name):
    """Stop a service"""
    service = CONFIG.get(service_name)
    if not service:
        print_colored(f"Unknown service: {service_name}", "red")
        return False
    
    print_colored(f"Stopping {service_name} service...", "blue")
    
    # Check if the service is running
    if not check_port("localhost", service["port"]):
        print_colored(f"✅ {service_name} is not running", "green")
        return True
    
    # Find processes by name or by port
    processes = get_process_by_name_and_port(service["process_name"], service["port"])
    
    if processes:
        print_colored(f"Found {len(processes)} {service_name} processes to terminate", "yellow")
        for proc in processes:
            kill_process(proc)
            print_colored(f"✅ Terminated {service_name} process with PID: {proc.pid}", "green")
    else:
        # If process not found by name, kill by port
        print_colored(f"No {service_name} processes found by name, killing processes by port {service['port']}", "yellow")
        kill_processes_by_port(service["port"])
    
    # Wait for port to be released
    for i in range(5):
        if not check_port("localhost", service["port"]):
            print_colored(f"✅ {service_name} stopped successfully", "green")
            return True
        time.sleep(1)
    
    print_colored(f"❌ {service_name} could not be stopped", "red")
    return False

def restart_service(service_name):
    """Restart a service"""
    print_colored(f"Restarting {service_name} service...", "blue")
    
    # Stop the service
    stop_service(service_name)
    
    # Start the service
    return start_service(service_name)

def check_service_status(service_name):
    """Check the status of a service"""
    service = CONFIG.get(service_name)
    if not service:
        print_colored(f"Unknown service: {service_name}", "red")
        return False
    
    port_in_use = check_port("localhost", service["port"])
    health_ok = service["health_check"]()
    
    status = "RUNNING" if port_in_use else "STOPPED"
    health = "HEALTHY" if health_ok else "UNHEALTHY"
    color = "green" if port_in_use and health_ok else "red" if not port_in_use else "yellow"
    
    print_colored(f"{service_name}: {status} / {health}", color)
    return port_in_use and health_ok

def check_all_services():
    """Check the status of all services"""
    print_colored("Checking all services...", "blue")
    
    all_healthy = True
    
    for service_name in CONFIG:
        healthy = check_service_status(service_name)
        all_healthy = all_healthy and healthy
    
    return all_healthy

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="GenAI Agent 3D Service Manager")
    parser.add_argument("command", choices=["start", "stop", "restart", "status"], help="Command to execute")
    parser.add_argument("--service", choices=list(CONFIG.keys()) + ["all"], default="all", help="Service to manage (default: all)")
    # For backwards compatibility, also accept positional service argument
    parser.add_argument("service_pos", nargs="?", choices=list(CONFIG.keys()) + ["all"], default=None, help=argparse.SUPPRESS)
    parser.add_argument("--force", action="store_true", help="Force restart even if the service is running and healthy")
    args = parser.parse_args()
    
    print_colored("\n" + "="*80, "header")
    print_colored(" GenAI Agent 3D Service Manager ".center(80, "="), "header")
    print_colored("="*80 + "\n", "header")
    
    # Determine which service to manage (positional arg has priority if provided)
    service = args.service_pos if args.service_pos is not None else args.service
    
    # Execute the command
    if args.command == "status":
        if service == "all":
            all_healthy = check_all_services()
            print_colored("\nOverall status: " + ("ALL SERVICES HEALTHY" if all_healthy else "SOME SERVICES UNHEALTHY"), "green" if all_healthy else "red")
        else:
            check_service_status(service)
    
    elif args.command == "start":
        if service == "all":
            redis_ok = start_service("redis", args.force)
            ollama_ok = start_service("ollama", args.force)
            backend_ok = start_service("backend", args.force)
            frontend_ok = start_service("frontend", args.force)
            
            all_ok = redis_ok and ollama_ok and backend_ok and frontend_ok
            
            print_colored("\nSummary:", "blue")
            print_colored(f"Redis: {'STARTED' if redis_ok else 'FAILED'}", "green" if redis_ok else "red")
            print_colored(f"Ollama: {'STARTED' if ollama_ok else 'FAILED'}", "green" if ollama_ok else "red")
            print_colored(f"Backend: {'STARTED' if backend_ok else 'FAILED'}", "green" if backend_ok else "red")
            print_colored(f"Frontend: {'STARTED' if frontend_ok else 'FAILED'}", "green" if frontend_ok else "red")
            
            if all_ok:
                url = "http://localhost:3000"
                print_colored(f"\n✅ All services started successfully! You can access the web interface at: {url}", "green")
                
                # Open browser
                if input("\nOpen browser to web interface? (y/n): ").lower() == 'y':
                    if platform.system() == 'Windows':
                        os.system(f'start {url}')
                    elif platform.system() == 'Darwin':  # macOS
                        os.system(f'open {url}')
                    else:  # Linux
                        os.system(f'xdg-open {url}')
            else:
                print_colored("\n❌ Some services failed to start", "red")
        else:
            start_service(service, args.force)
    
    elif args.command == "stop":
        if service == "all":
            # Stop in reverse order
            frontend_ok = stop_service("frontend")
            backend_ok = stop_service("backend")
            ollama_ok = stop_service("ollama")
            redis_ok = stop_service("redis")
            
            all_ok = redis_ok and ollama_ok and backend_ok and frontend_ok
            
            print_colored("\nSummary:", "blue")
            print_colored(f"Redis: {'STOPPED' if redis_ok else 'FAILED'}", "green" if redis_ok else "red")
            print_colored(f"Ollama: {'STOPPED' if ollama_ok else 'FAILED'}", "green" if ollama_ok else "red")
            print_colored(f"Backend: {'STOPPED' if backend_ok else 'FAILED'}", "green" if backend_ok else "red")
            print_colored(f"Frontend: {'STOPPED' if frontend_ok else 'FAILED'}", "green" if frontend_ok else "red")
            
            if all_ok:
                print_colored("\n✅ All services stopped successfully!", "green")
            else:
                print_colored("\n❌ Some services could not be stopped", "red")
        else:
            stop_service(service)
    
    elif args.command == "restart":
        if service == "all":
            # Stop all services first
            print_colored("Stopping all services...", "blue")
            frontend_ok = stop_service("frontend")
            backend_ok = stop_service("backend")
            ollama_ok = stop_service("ollama")
            redis_ok = stop_service("redis")
            
            # Start all services
            print_colored("\nStarting all services...", "blue")
            redis_ok = start_service("redis", args.force)
            ollama_ok = start_service("ollama", args.force)
            backend_ok = start_service("backend", args.force)
            frontend_ok = start_service("frontend", args.force)
            
            all_ok = redis_ok and ollama_ok and backend_ok and frontend_ok
            
            print_colored("\nSummary:", "blue")
            print_colored(f"Redis: {'RESTARTED' if redis_ok else 'FAILED'}", "green" if redis_ok else "red")
            print_colored(f"Ollama: {'RESTARTED' if ollama_ok else 'FAILED'}", "green" if ollama_ok else "red")
            print_colored(f"Backend: {'RESTARTED' if backend_ok else 'FAILED'}", "green" if backend_ok else "red")
            print_colored(f"Frontend: {'RESTARTED' if frontend_ok else 'FAILED'}", "green" if frontend_ok else "red")
            
            if all_ok:
                url = "http://localhost:3000"
                print_colored(f"\n✅ All services restarted successfully! You can access the web interface at: {url}", "green")
                
                # Open browser
                if input("\nOpen browser to web interface? (y/n): ").lower() == 'y':
                    if platform.system() == 'Windows':
                        os.system(f'start {url}')
                    elif platform.system() == 'Darwin':  # macOS
                        os.system(f'open {url}')
                    else:  # Linux
                        os.system(f'xdg-open {url}')
            else:
                print_colored("\n❌ Some services failed to restart", "red")
        else:
            restart_service(service)
    
    print_colored("\n" + "="*80, "header")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print_colored("\nOperation cancelled by user.", "yellow")
        sys.exit(130)
    except Exception as e:
        print_colored(f"\nUnexpected error: {e}", "red")
        sys.exit(1)


