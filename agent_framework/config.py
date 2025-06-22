"""Configuration management for the agent framework."""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional

# Load environment variables from .env file
load_dotenv()

class Config:
    """Manage configuration settings for the agent framework."""
    
    @staticmethod
    def get(key: str, default: Optional[str] = None) -> str:
        """
        Get a configuration value from environment variables.
        
        Args:
            key: The environment variable name
            default: Default value if key is not found
            
        Returns:
            The configuration value as a string
            
        Raises:
            ValueError: If the key is not found and no default is provided
        """
        value = os.getenv(key, default)
        if value is None:
            raise ValueError(f"Missing required environment variable: {key}")
        return value
    
    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        """Get a boolean configuration value."""
        value = os.getenv(key, '').lower()
        if value in ('true', '1', 't', 'y', 'yes'):
            return True
        if value in ('false', '0', 'f', 'n', 'no', ''):
            return False
        return default
    
    @staticmethod
    def get_int(key: str, default: int = 0) -> int:
        """Get an integer configuration value."""
        try:
            return int(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default
    
    @staticmethod
    def get_float(key: str, default: float = 0.0) -> float:
        """Get a float configuration value."""
        try:
            return float(os.getenv(key, str(default)))
        except (ValueError, TypeError):
            return default

# Common configuration values
OPENROUTER_API_KEY = Config.get('OPENROUTER_API_KEY')
MODEL_NAME = Config.get('MODEL_NAME', 'openai/gpt-4-turbo')
MODEL_TEMPERATURE = Config.get_float('MODEL_TEMPERATURE', 0.7)
MODEL_MAX_TOKENS = Config.get_int('MODEL_MAX_TOKENS', 4000)
