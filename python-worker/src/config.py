"""
Configuration management for the Python Portfolio Parser Worker.

Centralizes all configuration from environment variables with sensible defaults.
Optimized for containerized deployments where environment variables are injected.
"""

import os
import sys
import logging
from typing import Optional
from dataclasses import dataclass


@dataclass
class Config:
    """
    Configuration class for the worker.
    
    All configuration is loaded from environment variables with fallback defaults.
    This makes it easy to configure the worker in different environments
    (development, staging, production) without code changes.
    """
    
    # Redis Configuration
    redis_url: str = os.getenv('REDIS_URL', 'redis://localhost:6379')
    stream_key: str = os.getenv('REDIS_STREAM_KEY', 'portfolio:jobs')
    consumer_group: str = os.getenv('CONSUMER_GROUP', 'portfolio-workers')
    consumer_name: str = os.getenv('CONSUMER_NAME', 'python-worker-1')
    block_time: int = int(os.getenv('BLOCK_TIME', '1000'))  # milliseconds
    message_count: int = int(os.getenv('MESSAGE_COUNT', '10'))  # max messages per read
    
    # Logging Configuration
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    log_file: Optional[str] = os.getenv('LOG_FILE', None)  # None = no file logging
    
    def setup_logging(self) -> None:
        """
        Configure logging based on configuration.
        
        Supports both stdout (for containers) and file logging.
        Containers typically capture stdout, so file logging is optional.
        """
        # Convert log level string to logging constant
        numeric_level = getattr(logging, self.log_level.upper(), logging.INFO)
        
        # Create handlers
        handlers = [
            logging.StreamHandler(sys.stdout),  # Always log to stdout (for containers)
        ]
        
        # Add file handler if configured
        if self.log_file:
            handlers.append(logging.FileHandler(self.log_file))
        else:
            handlers.append(logging.NullHandler())
        
        # Configure logging
        logging.basicConfig(
            level=numeric_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=handlers
        )
    
    def validate(self) -> bool:
        """
        Validate configuration values.
        
        Returns:
            True if configuration is valid, raises ValueError otherwise
        """
        # Validate Redis URL format
        if not self.redis_url.startswith(('redis://', 'rediss://')):
            raise ValueError(f"Invalid Redis URL format: {self.redis_url}")
        
        # Validate numeric values
        if self.block_time < 0:
            raise ValueError(f"block_time must be non-negative, got: {self.block_time}")
        
        if self.message_count < 1:
            raise ValueError(f"message_count must be at least 1, got: {self.message_count}")
        
        # Validate log level
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level.upper() not in valid_levels:
            raise ValueError(f"Invalid log level: {self.log_level}. Must be one of {valid_levels}")
        
        return True


# Global configuration instance
_config: Optional[Config] = None


def get_config() -> Config:
    """
    Get the global configuration instance.
    
    Creates and validates configuration on first call.
    Subsequent calls return the same instance (singleton pattern).
    
    Returns:
        Config instance
    """
    global _config
    if _config is None:
        _config = Config()
        _config.validate()
        _config.setup_logging()
    return _config


def reset_config() -> None:
    """
    Reset the global configuration instance.
    
    Useful for testing to create a fresh configuration.
    """
    global _config
    _config = None

