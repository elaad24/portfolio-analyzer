"""
Main entry point for the Python Portfolio Parser Worker.

Consumes messages from Redis Streams, processes portfolio files,
and publishes results back to the message queue.

This is a minimal entry point that bootstraps the application.
All business logic is in separate modules.
"""

import sys
import signal
import logging

from .config import get_config
from .queue import MessageQueueWorker

logger = logging.getLogger(__name__)


def setup_signal_handlers(worker: MessageQueueWorker):
    """
    Setup signal handlers for graceful shutdown.
    
    Handles SIGTERM (used by Docker/Kubernetes) and SIGINT (Ctrl+C).
        
        Args:
        worker: MessageQueueWorker instance
    """
    def signal_handler(signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        # The worker will handle cleanup in its consume_messages loop
        sys.exit(0)
    
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)  # Docker/Kubernetes termination
    signal.signal(signal.SIGINT, signal_handler)   # Ctrl+C


def main():
    """Main entry point."""
    logger.info("=" * 60)
    logger.info("Python Portfolio Parser Worker")
    logger.info("=" * 60)
    
    # Get configuration (this also sets up logging)
    config = get_config()
    
    # Create worker
    worker = MessageQueueWorker(config=config)
    
    # Setup graceful shutdown handlers (for containers)
    setup_signal_handlers(worker)
    
    try:
        # Connect to Redis
        worker.connect()
        
        # Start consuming messages (this blocks until interrupted)
        worker.consume_messages()
        
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, shutting down...")
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
