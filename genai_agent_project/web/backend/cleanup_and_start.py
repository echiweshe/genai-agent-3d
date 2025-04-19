"""
Cleanup script that checks for existing server processes on port 8000
and terminates them before starting a new server.
"""

import os
import sys
import subprocess
import time
import signal
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def get_processes_on_port(port=8000):
    """Get list of processes using the specified port."""
    try:
        # On Windows, use netstat to find processes
        if os.name == 'nt':
            netstat_output = subprocess.check_output(
                f'netstat -ano | findstr :{port}', shell=True
            ).decode('utf-8')
            
            # Parse the output to get PIDs
            pids = set()
            for line in netstat_output.strip().split('\n'):
                # Split by whitespace and get the last item (PID)
                parts = [part for part in line.strip().split() if part]
                if len(parts) >= 5:
                    try:
                        pids.add(int(parts[4]))
                    except ValueError:
                        continue
            return list(pids)
            
        # On Unix-like systems, use lsof
        else:
            lsof_output = subprocess.check_output(
                f'lsof -i :{port} -t', shell=True
            ).decode('utf-8')
            return [int(pid) for pid in lsof_output.strip().split('\n') if pid]
    except subprocess.CalledProcessError:
        # No processes found
        return []

def kill_process(pid):
    """Kill a process with the given PID."""
    try:
        if os.name == 'nt':
            # On Windows, use taskkill
            subprocess.run(f'taskkill /F /PID {pid}', shell=True, check=True)
            logger.info(f"Successfully terminated process with PID {pid}")
        else:
            # On Unix-like systems, use kill
            os.kill(pid, signal.SIGTERM)
            logger.info(f"Sent SIGTERM to process with PID {pid}")
            
            # Give it a moment to terminate gracefully
            time.sleep(1)
            
            # Check if still running and force kill if necessary
            try:
                os.kill(pid, 0)  # This will raise an error if process is gone
                os.kill(pid, signal.SIGKILL)
                logger.info(f"Sent SIGKILL to process with PID {pid}")
            except OSError:
                pass  # Process already terminated
    except Exception as e:
        logger.error(f"Error killing process {pid}: {str(e)}")

def cleanup_port(port=8000):
    """Kill all processes using the specified port."""
    pids = get_processes_on_port(port)
    if not pids:
        logger.info(f"No processes found using port {port}")
        return

    logger.info(f"Found {len(pids)} process(es) using port {port}: {pids}")
    
    for pid in pids:
        # Don't kill our own process
        if pid != os.getpid():
            kill_process(pid)
    
    # Verify cleanup was successful
    remaining = get_processes_on_port(port)
    if remaining:
        logger.warning(f"Some processes are still using port {port}: {remaining}")
    else:
        logger.info(f"Successfully freed port {port}")
        # Wait a moment to ensure the socket is fully released
        time.sleep(1)

def start_server(args=None):
    """Start the server with the given arguments."""
    args = args or []
    server_script = os.path.join(os.path.dirname(__file__), "run_server.py")
    
    cmd = [sys.executable, server_script] + args
    logger.info(f"Starting server with command: {' '.join(cmd)}")
    
    try:
        # Use subprocess.run to wait for the server to complete
        subprocess.run(cmd)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error while running server: {str(e)}")

if __name__ == "__main__":
    # Get port from command line arguments, default to 8000
    port = 8000
    args = []
    
    # Process command line arguments
    i = 1
    has_auto_port = False
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == "--port" and i + 1 < len(sys.argv):
            port = int(sys.argv[i + 1])
            args.extend([arg, sys.argv[i + 1]])
            i += 2
        elif arg == "--auto-port":
            has_auto_port = True
            args.append(arg)
            i += 1
        else:
            args.append(arg)
            i += 1
    
    # Make sure auto-port is included
    if not has_auto_port:
        args.append("--auto-port")
    
    # Clean up any existing processes
    cleanup_port(port)
    
    # Start the server
    start_server(args)
