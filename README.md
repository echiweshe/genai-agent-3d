# GenAI Agent 3D - LLM Integration

This project enhances the GenAI Agent 3D platform with advanced Language Model (LLM) integration capabilities, allowing for AI-powered 3D content generation and manipulation.

## 🚀 Quick Start

To quickly fix all issues and start the application:

```bash
python fix_and_run.py
```

This script will:
1. Fix API route issues
2. Apply remaining fixes
3. Restart all services
4. Open the web interface

## 📋 Manual Setup

If you prefer to apply fixes manually, follow these steps:

### 1. Fix API Routes

```bash
python 05_fix_api_routes.py
```

This creates the necessary API endpoints for LLM integration.

### 2. Fix SVG Processor

```bash
python 06_fix_svg_processor.py
```

Fixes issues with the SVG processor code related to f-string backslash escaping.

### 3. Apply Final Fixes

```bash
python 08_final_fixes.py
```

Applies final fixes to ensure everything works correctly.

### 4. Restart Services

```bash
cd genai_agent_project
python manage_services.py restart all
```

## 📊 Features

- **LLM Integration**: Interact with language models from the user interface
- **Multi-Provider Support**: Works with Ollama by default, extensible to cloud providers
- **Testing Interface**: Dedicated LLM testing page with interactive UI
- **API Endpoints**: REST API for programmatic access to LLM capabilities
- **3D Tool Integration**: Use LLM outputs for 3D model and scene generation

## 🛠️ Configuration

LLM settings can be configured in two ways:

1. **Via Settings Page**: Navigate to the Settings page in the web UI
2. **Via Configuration File**: Edit `genai_agent_project/config/llm.yaml`

Default configuration:
```yaml
type: local
provider: ollama
model: llama3.2:latest
```

## 📚 Documentation

For detailed information on using the LLM features, refer to:

- [LLM Integration Guide](./docs/llm_integration.md) - Comprehensive guide to LLM features
- API documentation at `/api/docs` when the server is running

## 🧩 Components

- **LLM Service**: Core service for interacting with language models
- **API Routes**: FastAPI endpoints for LLM interaction
- **Test UI**: React-based user interface for testing LLM capabilities
- **Configuration System**: YAML-based configuration with UI editor

## 💻 Requirements

- Python 3.8+
- Node.js 14+
- Ollama (for local LLM inference)
- Blender 3.0+ (optional, for 3D modeling)

## 🔧 Development

For development and extending the LLM capabilities:

1. Clone the repository
2. Install dependencies in the Python virtual environment
3. Run the dev server: `python manage_services.py start all`
4. Make your changes
5. Test thoroughly

## 📝 License

This project is part of the GenAI Agent 3D platform. Use and distribution governed by the original license.

---

For support, please open an issue on the repository.
