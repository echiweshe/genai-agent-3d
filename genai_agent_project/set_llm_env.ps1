# PowerShell script to set environment variables and run a test
# Set environment variables
$env:OLLAMA_MODEL = "llama3"
$env:LLM_MODEL = "llama3"
$env:GENAI_LLM_MODEL = "llama3"

# Show the environment variables
Write-Host "Environment variables set:"
Write-Host "OLLAMA_MODEL = $env:OLLAMA_MODEL"
Write-Host "LLM_MODEL = $env:LLM_MODEL"
Write-Host "GENAI_LLM_MODEL = $env:GENAI_LLM_MODEL"

# Check if an example was provided
if ($args.Count -gt 0) {
    $example = $args[0]
    Write-Host "Running example: $example with llama3 model..."
    python run.py examples $example
}
else {
    Write-Host "No example specified."
    Write-Host "Usage: .\set_llm_env.ps1 <example_name>"
    Write-Host "Example: .\set_llm_env.ps1 test_json_generation"
}
