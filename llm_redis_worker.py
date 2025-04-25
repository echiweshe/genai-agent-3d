"""
LLM Redis Worker for processing LLM requests from the Redis message bus
"""

import asyncio
import json
import logging
import os
import time
import signal
import sys
from typing import Dict, Any, List, Optional

import aioredis

# Import the EnhancedLLMService
from genai_agent.services.enhanced_llm import EnhancedLLMService

logger = logging.getLogger(__name__)

class LLMRedisWorker:
    """
    Worker for processing LLM requests from Redis
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379", worker_id: str = None):
        """
        Initialize the LLM Redis Worker
        
        Args:
            redis_url: Redis connection URL
            worker_id: Unique worker ID (defaults to hostname + PID)
        """
        self.redis_url = redis_url
        self.worker_id = worker_id or f"{os.uname().nodename}-{os.getpid()}"
        self.redis = None
        self.pubsub = None
        self.llm_service = None
        self.running = False
        self.processing_task = None
        self.heartbeat_task = None
        
        # Register signal handlers for graceful shutdown
        for sig in (signal.SIGINT, signal.SIGTERM):
            signal.signal(sig, self._signal_handler)
        
        logger.info(f"LLM Redis Worker {self.worker_id} initializing")
    
    def _signal_handler(self, sig, frame):
        """Handle termination signals"""
        logger.info(f"Received signal {sig}, shutting down...")
        asyncio.create_task(self.stop())
    
    async def start(self):
        """Start the worker"""
        logger.info(f"Starting LLM Redis Worker {self.worker_id}")
        
        try:
            # Connect to Redis
            self.redis = await aioredis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Create LLM service
            self.llm_service = EnhancedLLMService()
            
            # Set up PubSub
            self.pubsub = self.redis.pubsub()
            await self.pubsub.subscribe("llm:requests", "llm:control")
            
            # Start processing
            self.running = True
            self.processing_task = asyncio.create_task(self._process_messages())
            self.heartbeat_task = asyncio.create_task(self._send_heartbeats())
            
            # Register worker
            await self._register_worker()
            
            logger.info(f"LLM Redis Worker {self.worker_id} started")
        
        except Exception as e:
            logger.error(f"Error starting worker: {str(e)}")
            await self.stop()
            raise
    
    async def stop(self):
        """Stop the worker"""
        logger.info(f"Stopping LLM Redis Worker {self.worker_id}")
        
        # Set running flag to false
        self.running = False
        
        # Unregister worker
        if self.redis:
            try:
                await self._unregister_worker()
            except Exception as e:
                logger.error(f"Error unregistering worker: {str(e)}")
        
        # Cancel tasks
        for task in [self.processing_task, self.heartbeat_task]:
            if task and not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        # Close connections
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
        
        if self.redis:
            await self.redis.close()
        
        logger.info(f"LLM Redis Worker {self.worker_id} stopped")
    
    async def _register_worker(self):
        """Register the worker in Redis"""
        worker_info = {
            "id": self.worker_id,
            "hostname": os.uname().nodename,
            "pid": os.getpid(),
            "start_time": time.time(),
            "status": "active",
            "providers": await self.llm_service.get_available_providers(),
            "last_heartbeat": time.time()
        }
        
        # Store worker info
        key = f"llm:workers:{self.worker_id}"
        await self.redis.hset(key, mapping=worker_info)
        
        # Set TTL
        await self.redis.expire(key, 300)  # 5 minutes
        
        # Publish registration event
        await self.redis.publish("llm:events", json.dumps({
            "type": "worker_registered",
            "worker_id": self.worker_id,
            "timestamp": time.time()
        }))
        
        logger.info(f"Worker {self.worker_id} registered")
    
    async def _unregister_worker(self):
        """Unregister the worker from Redis"""
        key = f"llm:workers:{self.worker_id}"
        await self.redis.delete(key)
        
        # Publish unregistration event
        await self.redis.publish("llm:events", json.dumps({
            "type": "worker_unregistered",
            "worker_id": self.worker_id,
            "timestamp": time.time()
        }))
        
        logger.info(f"Worker {self.worker_id} unregistered")
    
    async def _send_heartbeats(self):
        """Send periodic heartbeats to Redis"""
        try:
            while self.running:
                # Update heartbeat timestamp
                key = f"llm:workers:{self.worker_id}"
                await self.redis.hset(key, "last_heartbeat", time.time())
                await self.redis.hset(key, "status", "active")
                
                # Extend TTL
                await self.redis.expire(key, 300)  # 5 minutes
                
                # Wait for the next heartbeat interval
                await asyncio.sleep(60)  # Send heartbeat every minute
        
        except asyncio.CancelledError:
            logger.info("Heartbeat task cancelled")
        except Exception as e:
            logger.error(f"Error in heartbeat task: {str(e)}")
    
    async def _process_messages(self):
        """Process messages from the PubSub channels"""
        try:
            logger.info(f"Worker {self.worker_id} starting to process messages")
            
            while self.running:
                message = await self.pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                
                if not message:
                    await asyncio.sleep(0.01)  # Small delay to prevent CPU spin
                    continue
                
                if message["type"] == "message":
                    channel = message["channel"]
                    
                    try:
                        data = json.loads(message["data"])
                        
                        if channel == "llm:requests":
                            # Process LLM request
                            asyncio.create_task(self._handle_llm_request(data))
                        
                        elif channel == "llm:control":
                            # Process control request
                            asyncio.create_task(self._handle_control_request(data))
                    
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON in message: {message['data']}")
                    except Exception as e:
                        logger.error(f"Error processing message: {str(e)}")
            
            logger.info(f"Worker {self.worker_id} stopped processing messages")
        
        except asyncio.CancelledError:
            logger.info("Message processing task cancelled")
        except Exception as e:
            logger.error(f"Error in message processing task: {str(e)}")
    
    async def _handle_llm_request(self, data: Dict[str, Any]):
        """Handle an LLM request"""
        request_id = data.get("request_id")
        
        if not request_id:
            logger.error("Missing request_id in LLM request")
            return
        
        logger.info(f"Processing LLM request {request_id}")
        
        try:
            # Extract request details
            prompt = data.get("prompt", "")
            provider = data.get("provider")
            model = data.get("model")
            parameters = data.get("parameters", {})
            
            # Update status
            await self._update_request_status(request_id, "processing")
            
            # Process request with LLM service
            result = await self.llm_service.generate(
                prompt=prompt,
                provider=provider,
                model=model,
                parameters=parameters
            )
            
            # Prepare response
            response = {
                "request_id": request_id,
                "status": "completed",
                "provider": provider,
                "model": model,
                "timestamp": time.time()
            }
            
            # Add result or error
            if "error" in result:
                response["status"] = "error"
                response["error"] = result["error"]
            else:
                response["text"] = result.get("text", "")
                response["usage"] = result.get("usage", {})
            
            # Publish response
            await self.redis.publish("llm:responses", json.dumps(response))
            
            logger.info(f"Completed LLM request {request_id}")
        
        except Exception as e:
            logger.error(f"Error processing LLM request {request_id}: {str(e)}")
            
            # Publish error response
            error_response = {
                "request_id": request_id,
                "status": "error",
                "error": f"Worker error: {str(e)}",
                "timestamp": time.time()
            }
            
            await self.redis.publish("llm:responses", json.dumps(error_response))
    
    async def _handle_control_request(self, data: Dict[str, Any]):
        """Handle a control request"""
        request_id = data.get("request_id")
        action = data.get("action")
        
        if not request_id:
            logger.error("Missing request_id in control request")
            return
        
        logger.info(f"Processing control request {request_id} (action: {action})")
        
        try:
            if action == "get_providers":
                # Get available providers
                providers = await self.llm_service.get_available_providers()
                
                # Publish response
                response = {
                    "request_id": request_id,
                    "status": "completed",
                    "providers": providers,
                    "timestamp": time.time()
                }
                
                await self.redis.publish("llm:responses", json.dumps(response))
            
            elif action == "estimate_cost":
                # Estimate cost for a request
                prompt = data.get("prompt", "")
                provider = data.get("provider")
                model = data.get("model")
                
                # Get cost estimate
                estimate = await self.llm_service.estimate_cost(prompt, provider, model)
                
                # Publish response
                response = {
                    "request_id": request_id,
                    "status": "completed",
                    "estimate": estimate,
                    "timestamp": time.time()
                }
                
                await self.redis.publish("llm:responses", json.dumps(response))
            
            elif action == "worker_status":
                # Return worker status
                response = {
                    "request_id": request_id,
                    "status": "completed",
                    "worker": {
                        "id": self.worker_id,
                        "status": "active",
                        "uptime": time.time() - (await self.redis.hget(f"llm:workers:{self.worker_id}", "start_time")),
                        "providers": await self.llm_service.get_available_providers()
                    },
                    "timestamp": time.time()
                }
                
                await self.redis.publish("llm:responses", json.dumps(response))
            
            else:
                logger.warning(f"Unknown control action: {action}")
                
                # Publish error response
                error_response = {
                    "request_id": request_id,
                    "status": "error",
                    "error": f"Unknown control action: {action}",
                    "timestamp": time.time()
                }
                
                await self.redis.publish("llm:responses", json.dumps(error_response))
        
        except Exception as e:
            logger.error(f"Error processing control request {request_id}: {str(e)}")
            
            # Publish error response
            error_response = {
                "request_id": request_id,
                "status": "error",
                "error": f"Worker error: {str(e)}",
                "timestamp": time.time()
            }
            
            await self.redis.publish("llm:responses", json.dumps(error_response))
    
    async def _update_request_status(self, request_id: str, status: str):
        """Update the status of a request in Redis"""
        key = f"llm:requests:{request_id}"
        
        try:
            # Update status and timestamp
            await self.redis.hset(key, mapping={
                "status": status,
                "updated_at": time.time(),
                "worker_id": self.worker_id
            })
            
            # Set TTL (requests expire after 1 hour)
            await self.redis.expire(key, 3600)
            
            # Publish status update event
            await self.redis.publish("llm:events", json.dumps({
                "type": "request_status_updated",
                "request_id": request_id,
                "status": status,
                "worker_id": self.worker_id,
                "timestamp": time.time()
            }))
        
        except Exception as e:
            logger.error(f"Error updating request status: {str(e)}")

async def run_worker():
    """Run the LLM Redis Worker"""
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create worker
    worker = LLMRedisWorker()
    
    try:
        # Start worker
        await worker.start()
        
        # Keep running until stopped
        while worker.running:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received, shutting down...")
    except Exception as e:
        logger.error(f"Error running worker: {str(e)}")
    finally:
        # Stop worker
        await worker.stop()

def main():
    """Entry point for the LLM Redis Worker"""
    asyncio.run(run_worker())

if __name__ == "__main__":
    main()
