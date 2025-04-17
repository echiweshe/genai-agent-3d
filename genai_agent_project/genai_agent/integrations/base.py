"""
Base class for external tool integrations
"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger(__name__)

class BaseIntegration(ABC):
    """Base class for all external tool integrations"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the integration
        
        Args:
            config: Integration configuration
        """
        self.config = config or {}
        self._is_available = False
        self._version = None
        self.name = self.__class__.__name__
        
        # Try to initialize the integration
        try:
            self._initialize()
            self._is_available = True
            logger.info(f"Integration {self.name} initialized successfully (version: {self._version})")
        except Exception as e:
            logger.warning(f"Failed to initialize integration {self.name}: {str(e)}")
            self._is_available = False
    
    @abstractmethod
    def _initialize(self):
        """Initialize the integration and check if it's available"""
        pass
    
    @property
    def is_available(self) -> bool:
        """Check if the integration is available"""
        return self._is_available
    
    @property
    def version(self) -> Optional[str]:
        """Get the version of the integrated tool"""
        return self._version
    
    def get_status(self) -> Dict[str, Any]:
        """Get the status of the integration"""
        return {
            'name': self.name,
            'available': self.is_available,
            'version': self.version
        }
    
    def get_capabilities(self) -> List[str]:
        """Get the list of capabilities provided by this integration"""
        return []
    
    @abstractmethod
    async def execute(self, operation: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an operation using the integrated tool
        
        Args:
            operation: Operation to execute
            parameters: Operation parameters
            
        Returns:
            Operation result
        """
        pass
