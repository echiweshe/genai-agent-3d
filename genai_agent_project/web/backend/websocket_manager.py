"""
WebSocket Manager for real-time communication
"""

import logging
import json
import asyncio
from typing import Dict, Any, List, Callable, Awaitable, Optional
from fastapi import WebSocket

logger = logging.getLogger(__name__)

class WebSocketManager:
    """
    WebSocket connection manager for handling real-time communication
    """
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.listeners: Dict[str, List[Callable[[Dict[str, Any]], Awaitable[None]]]] = {}
    
    async def connect(self, client_id: str, websocket: WebSocket):
        """
        Connect a client
        
        Args:
            client_id: Client identifier
            websocket: WebSocket connection
        """
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"Client connected: {client_id}")
    
    def disconnect(self, client_id: str):
        """
        Disconnect a client
        
        Args:
            client_id: Client identifier
        """
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            logger.info(f"Client disconnected: {client_id}")
    
    async def send_message(self, client_id: str, message: Dict[str, Any]):
        """
        Send a message to a specific client
        
        Args:
            client_id: Client identifier
            message: Message to send
        """
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)
    
    async def broadcast(self, message: Dict[str, Any], exclude: Optional[str] = None):
        """
        Broadcast a message to all connected clients
        
        Args:
            message: Message to broadcast
            exclude: Client ID to exclude from broadcast
        """
        for client_id, websocket in self.active_connections.items():
            if exclude and client_id == exclude:
                continue
                
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error sending message to client {client_id}: {str(e)}")
    
    def add_listener(self, event_type: str, callback: Callable[[Dict[str, Any]], Awaitable[None]]):
        """
        Add a listener for a specific event type
        
        Args:
            event_type: Event type to listen for
            callback: Callback function to call when the event is received
        """
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        
        self.listeners[event_type].append(callback)
    
    async def handle_message(self, client_id: str, message: Dict[str, Any]):
        """
        Handle a message from a client
        
        Args:
            client_id: Client identifier
            message: Message received
        """
        # Check message type
        message_type = message.get('type')
        
        if not message_type:
            logger.warning(f"Received message without type from client {client_id}")
            return
        
        # Call listeners for this message type
        if message_type in self.listeners:
            for callback in self.listeners[message_type]:
                try:
                    await callback({
                        'client_id': client_id,
                        'message': message
                    })
                except Exception as e:
                    logger.error(f"Error in listener callback: {str(e)}")
    
    async def listen(self, client_id: str, websocket: WebSocket):
        """
        Listen for messages from a client
        
        Args:
            client_id: Client identifier
            websocket: WebSocket connection
        """
        try:
            while True:
                # Wait for a message from the client
                message = await websocket.receive_json()
                
                # Handle the message
                await self.handle_message(client_id, message)
        except Exception as e:
            logger.error(f"WebSocket error for client {client_id}: {str(e)}")
            self.disconnect(client_id)
