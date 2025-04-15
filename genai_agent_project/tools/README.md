# GenAI Agent Tools

This directory contains utility tools to help with the development and maintenance of the GenAI Agent for 3D Modeling.

## Integration Tools

### SceneX Integration (`integrate_scenex.py`)

This script helps integrate your existing SceneX code into the GenAI Agent.

**Usage:**

```bash
# Automatically detect SceneX repository
python integrate_scenex.py

# Specify SceneX repository path
python integrate_scenex.py --repo /path/to/scenex/repo

# Specify target directory
python integrate_scenex.py --target /path/to/genai_agent
```

The integration process:
1. Analyzes your SceneX repository to identify coordinate and animation-related code
2. Copies the key files to a `scenex_integration` directory
3. Creates an integration module to help with using your SceneX code

After running the integration, you'll need to:
1. Review the integrated files
2. Update the SceneXTool class to use your integrated code
3. Test the integration with examples

## Adding New Tools

To add a new utility tool:

1. Create a new Python script in this directory
2. Add usage instructions to this README
3. Consider adding the tool to the main `run.py` script in the parent directory
