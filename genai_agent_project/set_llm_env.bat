@echo off
set OLLAMA_MODEL=llama3
set LLM_MODEL=llama3
set GENAI_LLM_MODEL=llama3
echo Environment variables set:
echo OLLAMA_MODEL=%OLLAMA_MODEL%
echo LLM_MODEL=%LLM_MODEL%
echo GENAI_LLM_MODEL=%GENAI_LLM_MODEL%
echo.
echo Run your tests with these variables by using this prefix.
echo For example: call set_llm_env.bat && python run.py examples test_json_generation
