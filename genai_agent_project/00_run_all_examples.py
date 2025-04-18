#!/usr/bin/env python
"""
Run All Examples with Extended Timeout

This script runs all example scripts in the examples/ directory
with an extended timeout to prevent premature termination.
"""

import os
import subprocess
import sys
import time
from colorama import init, Fore, Style

# Initialize colorama
init()

# Configuration
LIVE_OUTPUT = True  # Show output in real-time
SCRIPT_TIMEOUT_SECONDS = 300  # 5 minutes per script
EXAMPLES_DIR = os.path.join(os.path.dirname(__file__), "examples")

def print_color(text, color=Fore.WHITE):
    """Print colored text"""
    print(f"{color}{text}{Style.RESET_ALL}")

def run_script(script_path):
    """Run a Python script with extended timeout"""
    script_name = os.path.basename(script_path)
    print_color(f"\n🚀 Running: {script_name}", Fore.CYAN)
    
    start_time = time.time()
    
    try:
        # Set additional environment variables for the subprocess
        env = os.environ.copy()
        env["LLM_MODEL"] = "llama3"
        env["LLM_TIMEOUT"] = "300"
        env["OLLAMA_MODEL"] = "llama3"
        
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=os.path.dirname(script_path),
            capture_output=not LIVE_OUTPUT,
            text=True,
            timeout=SCRIPT_TIMEOUT_SECONDS,
            env=env
        )
        
        elapsed = time.time() - start_time
        
        # Process and display results
        if result.returncode == 0:
            print_color(f"\n✅ Success: {script_name} completed in {elapsed:.2f} seconds", Fore.GREEN)
            
            # Parse output to summarize results if not already showing live
            if not LIVE_OUTPUT and result.stdout:
                print(result.stdout)
            
            if result.stderr:
                print_color(f"\n⚠️ STDERR:", Fore.YELLOW)
                print(result.stderr)
            
            return True, parse_results(result.stdout) if not LIVE_OUTPUT else {}
        else:
            print_color(f"\n❌ Failed: {script_name} exited with code {result.returncode} after {elapsed:.2f} seconds", Fore.RED)
            
            if not LIVE_OUTPUT:
                print(result.stdout)
            
            if result.stderr:
                print_color(f"\n⚠️ STDERR:", Fore.YELLOW)
                print(result.stderr)
            
            return False, {}
    
    except subprocess.TimeoutExpired:
        elapsed = time.time() - start_time
        print_color(f"⏰ Timeout while running {script_path} after {elapsed:.2f} seconds", Fore.YELLOW)
        return False, {"timeout": True}
    
    except Exception as e:
        elapsed = time.time() - start_time
        print_color(f"❌ Error while running {script_path} after {elapsed:.2f} seconds:\n{e}", Fore.RED)
        return False, {"error": str(e)}

def parse_results(output):
    """Parse output to extract results (customize based on output format)"""
    results = {}
    
    # This is a simple example - enhance based on your output format
    if "success" in output.lower():
        results["success"] = True
    
    if "error" in output.lower():
        results["error"] = True
    
    return results

def main():
    """Main function to run all examples"""
    print_color("🔍 GenAI Agent 3D - Example Test Runner", Fore.CYAN)
    
    if not os.path.isdir(EXAMPLES_DIR):
        print_color(f"❌ Examples directory not found: {EXAMPLES_DIR}", Fore.RED)
        return
    
    # Get all Python files in the examples directory
    py_files = sorted(f for f in os.listdir(EXAMPLES_DIR) if f.endswith(".py"))
    if not py_files:
        print_color("📭 No Python scripts found in examples/", Fore.YELLOW)
        return
    
    print_color(f"📁 Found {len(py_files)} example scripts to run", Fore.CYAN)
    
    # Run all scripts and collect results
    success_count = 0
    results = {}
    
    for file in py_files:
        full_path = os.path.join(EXAMPLES_DIR, file)
        success, script_results = run_script(full_path)
        
        if success:
            success_count += 1
        
        results[file] = {
            "success": success,
            **script_results
        }
    
    # Summarize results
    print_color(f"\n✅ Done: {success_count}/{len(py_files)} scripts ran successfully.", Fore.GREEN if success_count == len(py_files) else Fore.YELLOW)

if __name__ == "__main__":
    start = time.time()
    main()
    duration = time.time() - start
    print_color(f"🕒 Elapsed time: {duration:.2f} seconds", Fore.CYAN)
