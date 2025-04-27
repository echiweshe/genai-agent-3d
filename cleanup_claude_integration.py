#!/usr/bin/env python3
"""
Cleanup Claude Integration Scripts

This script organizes and ensures consistency across all Claude API integration scripts
and documentation in the GenAI Agent 3D project.
"""

import os
import sys
import shutil
import re
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """Main function"""
    project_root = Path(__file__).parent.absolute()
    
    # Create scripts directory if it doesn't exist
    scripts_dir = project_root / "scripts" / "claude"
    scripts_dir.mkdir(exist_ok=True, parents=True)
    
    # Move and organize scripts
    script_files = [
        "fix_claude_api_key.py",
        "fix_claude_integration.py",
        "test_claude_api.py",
        "set_claude_default.py",
        "check_claude_key.py",
        "restart_claude.py"
    ]
    
    # Documentation files
    doc_files = [
        "CLAUDE_API_FIX.md",
        "CLAUDE_FIX_README.md",
        "CLAUDE_SETUP.md"
    ]
    
    # Check for existing scripts and move them
    for script in script_files:
        source_path = project_root / script
        if source_path.exists():
            # Create a copy in the scripts directory
            target_path = scripts_dir / script
            shutil.copy2(source_path, target_path)
            logger.info(f"Copied {script} to {target_path}")
    
    # Create a symlink to run the scripts from the root directory
    for script in ["fix_claude_integration.py", "test_claude_api.py", "set_claude_default.py"]:
        source_path = project_root / script
        if source_path.exists():
            # Ensure the script is executable
            os.chmod(source_path, 0o755)
            logger.info(f"Made {script} executable")
    
    # Create a unified documentation file
    unified_doc_path = project_root / "docs" / "CLAUDE_INTEGRATION.md"
    unified_doc_path.parent.mkdir(exist_ok=True)
    
    # Combine documentation files
    content = "# Claude Integration for GenAI Agent 3D\n\n"
    content += "This comprehensive guide provides information about Claude API integration in the GenAI Agent 3D project.\n\n"
    
    # Add table of contents
    content += "## Table of Contents\n\n"
    content += "1. [Overview](#overview)\n"
    content += "2. [Issues Fixed](#issues-fixed)\n"
    content += "3. [How to Apply the Fix](#how-to-apply-the-fix)\n"
    content += "4. [Technical Details](#technical-details)\n"
    content += "5. [Troubleshooting](#troubleshooting)\n"
    content += "6. [Available Claude Models](#available-claude-models)\n"
    content += "7. [API Usage and Costs](#api-usage-and-costs)\n"
    content += "8. [Setting Claude as Default](#setting-claude-as-default)\n"
    content += "9. [Command Reference](#command-reference)\n\n"
    
    # Add overview
    content += "## Overview\n\n"
    content += "GenAI Agent 3D now integrates with Anthropic's Claude AI models, providing enhanced capabilities for generating 3D content, diagrams, and more. Claude offers superior performance in understanding complex instructions and generating high-quality content.\n\n"
    
    # Incorporate content from existing documentation files
    for doc_file in doc_files:
        doc_path = project_root / doc_file
        if doc_path.exists():
            with open(doc_path, 'r', encoding='utf-8') as f:
                doc_content = f.read()
                
                # Extract headings and content, skipping the main heading
                lines = doc_content.split('\n')
                skip_first_heading = True
                for line in lines:
                    if line.startswith('#') and skip_first_heading:
                        skip_first_heading = False
                        continue
                    
                    # Add the line to the unified document
                    if line.startswith('##'):
                        # Replace headings with our own structure
                        if "issues fixed" in line.lower():
                            continue  # We'll add this section later
                        if "how to" in line.lower() or "apply" in line.lower():
                            continue  # We'll add this section later
                        if "technical details" in line.lower():
                            continue  # We'll add this section later
                        if "troubleshooting" in line.lower():
                            continue  # We'll add this section later
                        if "models" in line.lower():
                            continue  # We'll add this section later
                        if "costs" in line.lower() or "usage" in line.lower():
                            continue  # We'll add this section later
                    
                    # content += line + "\n"
    
    # Add issues fixed section from CLAUDE_API_FIX.md
    api_fix_path = project_root / "CLAUDE_API_FIX.md"
    if api_fix_path.exists():
        with open(api_fix_path, 'r', encoding='utf-8') as f:
            api_fix_content = f.read()
            
            # Extract issues fixed section
            issues_match = re.search(r'## Issues Fixed\s+(.+?)(?=##)', api_fix_content, re.DOTALL)
            if issues_match:
                content += "## Issues Fixed\n\n"
                content += issues_match.group(1).strip() + "\n\n"
            
            # Extract how to apply section
            how_to_match = re.search(r'## How to Apply the Fix\s+(.+?)(?=##)', api_fix_content, re.DOTALL)
            if how_to_match:
                content += "## How to Apply the Fix\n\n"
                content += how_to_match.group(1).strip() + "\n\n"
            
            # Extract technical details section
            technical_match = re.search(r'## Technical Details\s+(.+?)(?=##)', api_fix_content, re.DOTALL)
            if technical_match:
                content += "## Technical Details\n\n"
                content += technical_match.group(1).strip() + "\n\n"
            
            # Extract troubleshooting section
            troubleshooting_match = re.search(r'## Troubleshooting\s+(.+?)(?=##)', api_fix_content, re.DOTALL)
            if troubleshooting_match:
                content += "## Troubleshooting\n\n"
                content += troubleshooting_match.group(1).strip() + "\n\n"
            
            # Extract available models section
            models_match = re.search(r'## Available Claude Models\s+(.+?)(?=##)', api_fix_content, re.DOTALL)
            if models_match:
                content += "## Available Claude Models\n\n"
                content += models_match.group(1).strip() + "\n\n"
            
            # Extract API usage and costs section
            costs_match = re.search(r'## API Usage and Costs\s+(.+?)(?=$)', api_fix_content, re.DOTALL)
            if costs_match:
                content += "## API Usage and Costs\n\n"
                content += costs_match.group(1).strip() + "\n\n"
    
    # Add setting claude as default section
    content += "## Setting Claude as Default\n\n"
    content += "To set Claude as the default LLM provider, you can use the provided script:\n\n"
    content += "```bash\n"
    content += "python set_claude_default.py\n"
    content += "```\n\n"
    content += "This script will update both the `.env` file and `config.yaml` with the following settings:\n\n"
    content += "```\n"
    content += "LLM_PROVIDER=anthropic\n"
    content += "LLM_MODEL=claude-3-sonnet-20240229\n"
    content += "LLM_TYPE=cloud\n"
    content += "```\n\n"
    content += "You can also manually edit these files to set Claude as the default.\n\n"
    
    # Add command reference section
    content += "## Command Reference\n\n"
    content += "The following scripts are available for working with Claude integration:\n\n"
    content += "| Script | Description |\n"
    content += "|--------|-------------|\n"
    content += "| `fix_claude_integration.py` | Fixes Claude API integration issues |\n"
    content += "| `test_claude_api.py` | Tests the Claude API integration |\n"
    content += "| `set_claude_default.py` | Sets Claude as the default LLM provider |\n"
    content += "| `check_claude_key.py` | Checks if the Claude API key is properly set |\n"
    content += "| `restart_claude.py` | Restarts services with Claude as the default provider |\n\n"
    content += "These scripts are located in both the project root and the `scripts/claude/` directory.\n\n"
    
    # Write the unified documentation
    with open(unified_doc_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    logger.info(f"Created unified documentation at {unified_doc_path}")
    
    print("\n✅ Cleanup completed successfully!")
    print(f"Unified documentation: {unified_doc_path}")
    print(f"Scripts directory: {scripts_dir}")
    
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
