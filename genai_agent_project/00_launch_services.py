import os
import json
import subprocess
import platform
import time

def create_vscode_terminal_config(terminal_name, command, working_dir):
    """Create a configuration for a new VS Code terminal"""
    return {
        "name": terminal_name,
        "command": command,
        "workingDirectory": working_dir
    }

def main():
    # Base directory of the project
    base_dir = r"C:\ZB_Share\Labs\src\CluadeMCP\genai-agent-3d\genai_agent_project"
    
    # Define all the terminals and commands we need
    terminals = [
        # Redis server
        create_vscode_terminal_config(
            "Redis Server",
            "redis-server",
            base_dir
        ),
        
        # Redis monitoring (optional, for debugging)
        create_vscode_terminal_config(
            "Redis Monitor",
            "redis-cli monitor",
            base_dir
        ),
        
        # Ollama server
        create_vscode_terminal_config(
            "Ollama Server",
            "ollama serve",
            base_dir
        ),
        
        # Backend server
        create_vscode_terminal_config(
            "Backend Server",
            "python run_server.py",
            os.path.join(base_dir, "web", "backend")
        ),
        
        # Frontend server
        create_vscode_terminal_config(
            "Frontend Server",
            "npm start",
            os.path.join(base_dir, "web", "frontend")
        ),
        
        # Agent Core
        create_vscode_terminal_config(
            "Agent Core",
            "python run.py shell",
            base_dir
        ),
    ]
    
    # Get the path to the VS Code settings file
    if platform.system() == "Windows":
        settings_path = os.path.join(os.environ["APPDATA"], "Code", "User", "settings.json")
    elif platform.system() == "Darwin":  # macOS
        settings_path = os.path.expanduser("~/Library/Application Support/Code/User/settings.json")
    else:  # Linux
        settings_path = os.path.expanduser("~/.config/Code/User/settings.json")
    
    # Create the VS Code command to execute
    commands = []
    
    # Add command to close all terminals first
    commands.append("workbench.action.terminal.killAll")
    
    # Command to create each terminal
    for terminal in terminals:
        commands.append("workbench.action.terminal.new")
        commands.append({
            "command": "workbench.action.terminal.renameWithArg",
            "args": {"name": terminal["name"]}
        })
        
        # Set working directory
        if terminal["workingDirectory"]:
            commands.append({
                "command": "workbench.action.terminal.sendSequence",
                "args": {"text": f"cd {terminal['workingDirectory']}\n"}
            })
        
        # Execute the command
        if terminal["command"]:
            commands.append({
                "command": "workbench.action.terminal.sendSequence",
                "args": {"text": f"{terminal['command']}\n"}
            })
    
    # Generate the keyboard shortcut file content
    keyboard_shortcut = {
        "key": "ctrl+shift+l",  # You can change this shortcut
        "command": "extension.multiCommand.execute",
        "args": {"command": "genai.launchAllProcesses"}
    }
    
    multi_command_config = {
        "multiCommand.commands": [
            {
                "command": "genai.launchAllProcesses",
                "sequence": commands
            }
        ]
    }
    
    # Save the multi-command configuration
    try:
        # Read the existing settings file
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        # Update or add the multiCommand settings
        if "multiCommand.commands" in settings:
            # Check if our command already exists
            command_exists = False
            for i, cmd in enumerate(settings["multiCommand.commands"]):
                if cmd.get("command") == "genai.launchAllProcesses":
                    settings["multiCommand.commands"][i]["sequence"] = commands
                    command_exists = True
                    break
            
            if not command_exists:
                settings["multiCommand.commands"].append(multi_command_config["multiCommand.commands"][0])
        else:
            settings["multiCommand.commands"] = multi_command_config["multiCommand.commands"]
        
        # Write back the updated settings
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=4)
        
        print(f"VS Code configuration updated successfully!")
        print(f"Press Ctrl+Shift+L to launch all terminals.")
        print(f"NOTE: You need to have the 'Multi Command' extension installed in VS Code.")
        
    except Exception as e:
        print(f"Error updating VS Code settings: {e}")
        print("Manual launch instructions:")
        print("\nTo manually launch all services, run the following commands in separate terminals:")
        
        for terminal in terminals:
            print(f"\n--- Terminal: {terminal['name']} ---")
            print(f"cd {terminal['workingDirectory']}")
            print(f"{terminal['command']}")

    # Create a batch file as an alternative launch method
    batch_file_path = os.path.join(base_dir, "launch_all_services.bat")
    with open(batch_file_path, 'w') as batch_file:
        batch_file.write("@echo off\n")
        batch_file.write("echo Launching GenAI Agent 3D services...\n\n")
        
        for i, terminal in enumerate(terminals):
            if i == 0:  # First service (Redis)
                batch_file.write(f"start \"Redis Server\" cmd /k \"cd /d {terminal['workingDirectory']} && {terminal['command']}\"\n")
                batch_file.write("timeout /t 2 > nul\n")  # Wait for Redis to start
            else:
                batch_file.write(f"start \"{terminal['name']}\" cmd /k \"cd /d {terminal['workingDirectory']} && {terminal['command']}\"\n")
                batch_file.write("timeout /t 1 > nul\n")  # Brief pause between launches
    
    print(f"\nBatch file created at: {batch_file_path}")
    print("You can run this batch file to launch all services in separate command prompt windows.")

if __name__ == "__main__":
    main()
