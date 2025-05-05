_path}")
            
            # 3. Apply animations
            animated_path = os.path.join(job_dir, "animated.blend")
            await self._run_blender_script(
                "scenex_animation.py",
                [model_path, animated_path],
                "Applying animations"
            )
            
            logger.info(f"Animated scene saved to {animated_path}")
            
            # 4. Render video
            render_quality = options.get("render_quality", "medium")
            await self._run_blender_script(
                "video_renderer.py",
                [animated_path, output_path, render_quality],
                "Rendering video"
            )
            
            logger.info(f"Video rendered to {output_path}")
            
            return {
                "status": "success",
                "output_path": output_path,
                "job_id": job_id
            }
            
        except Exception as e:
            logger.error(f"Pipeline error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "job_id": job_id
            }
        finally:
            # Cleanup temporary files if needed
            if self.config.get("cleanup_temp", True):
                shutil.rmtree(job_dir)
    
    async def _run_blender_script(self, script_name, args, description):
        """Run a Blender script as a subprocess."""
        script_dir = self.config.get("script_dir", "scripts")
        script_path = os.path.join(script_dir, script_name)
        
        blender_path = self.config.get("blender_path", "blender")
        
        cmd = [
            blender_path,
            "--background",
            "--python", script_path,
            "--"
        ] + args
        
        logger.info(f"{description}: {' '.join(cmd)}")
        
        # Run the process
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Capture output
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode()
            logger.error(f"Blender process failed: {error_msg}")
            raise RuntimeError(f"Blender process failed: {error_msg[:500]}...")
        
        return True
```

### Phase 2: Infrastructure Integration (2-3 Weeks)

Once the core pipeline is working, we'll integrate it with the basic LangChain setup and Redis messaging system.

#### Step 1: LangChain Manager for SVG Generation

```python
# langchain_manager.py
import asyncio
import logging
from langchain.chat_models import ChatOpenAI, ChatAnthropic, ChatOllama
from langchain.schema import HumanMessage
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

logger = logging.getLogger(__name__)

class LangChainManager:
    """Manager for LangChain operations focused on SVG generation."""
    
    def __init__(self, config=None):
        """Initialize the LangChain manager."""
        self.config = config or {}
        
        # Set up LLM providers
        self.providers = {}
        self._initialize_providers()
        
        # Set up memory
        self.memories = {}
    
    def _initialize_providers(self):
        """Initialize LLM providers based on available API keys."""
        import os
        
        # OpenAI
        openai_api_key = os.environ.get("OPENAI_API_KEY")
        if openai_api_key:
            self.providers["openai"] = ChatOpenAI(
                api_key=openai_api_key,
                temperature=0.7
            )
            logger.info("Initialized OpenAI provider")
        
        # Anthropic/Claude
        anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        if anthropic_api_key:
            self.providers["claude"] = ChatAnthropic(
                api_key=anthropic_api_key,
                temperature=0.7
            )
            logger.info("Initialized Claude provider")
        
        # Ollama (local models)
        try:
            import requests
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                self.providers["ollama"] = ChatOllama(model="llama3")
                logger.info("Initialized Ollama provider")
        except Exception as e:
            logger.warning(f"Ollama initialization failed: {str(e)}")
    
    def get_memory(self, session_id):
        """Get or create memory for a session."""
        if session_id not in self.memories:
            self.memories[session_id] = ConversationBufferMemory(
                memory_key="chat_history", 
                return_messages=True
            )
        
        return self.memories[session_id]
    
    def get_provider(self, provider_name):
        """Get a provider by name."""
        provider = self.providers.get(provider_name)
        if not provider:
            available = list(self.providers.keys())
            if available:
                provider = self.providers[available[0]]
                logger.warning(f"Provider {provider_name} not available, using {available[0]}")
            else:
                raise ValueError("No LLM providers available")
        
        return provider
    
    async def generate_svg(self, concept, provider_name="claude", session_id=None):
        """Generate an SVG diagram based on a concept."""
        provider = self.get_provider(provider_name)
        
        # Create prompt
        svg_prompt = """Create an SVG diagram that represents the following concept:
        
{concept}
        
Requirements:
- Use standard SVG elements (rect, circle, path, text, etc.)
- Include appropriate colors and styling
- Ensure the diagram is clear and readable
- Add proper text labels
- Use viewBox="0 0 800 600" for dimensions
- Wrap the entire SVG in <svg> tags
- Do not include any explanation, just the SVG code
        
SVG Diagram:"""
        
        formatted_prompt = svg_prompt.format(concept=concept)
        
        # Generate with retry logic
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                # Create messages
                messages = [HumanMessage(content=formatted_prompt)]
                
                # Add memory if session_id provided
                if session_id:
                    memory = self.get_memory(session_id)
                    memory_messages = memory.load_memory_variables({}).get("chat_history", [])
                    messages = memory_messages + messages
                
                # Generate response
                response = await provider.agenerate([messages])
                svg_text = response.generations[0][0].text
                
                # Save to memory if session_id provided
                if session_id:
                    memory.save_context(
                        {"input": formatted_prompt},
                        {"output": svg_text}
                    )
                
                # Extract SVG content
                if "<svg" in svg_text and "</svg>" in svg_text:
                    import re
                    svg_match = re.search(r'(<svg[\s\S]*?</svg>)', svg_text, re.DOTALL)
                    if svg_match:
                        return svg_match.group(1)
                    return svg_text
                else:
                    if attempt < max_retries:
                        logger.warning(f"Invalid SVG response, retrying ({attempt+1}/{max_retries})")
                        continue
                    raise ValueError("Generated content is not valid SVG")
                
            except Exception as e:
                if attempt < max_retries:
                    logger.warning(f"Generation error, retrying ({attempt+1}/{max_retries}): {str(e)}")
                    continue
                raise
        
        raise RuntimeError("Failed to generate valid SVG after multiple attempts")
```
