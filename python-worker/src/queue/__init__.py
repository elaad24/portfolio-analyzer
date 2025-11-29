"""
Message queue integration module.

Handles Redis Streams connection, message consumption, and result publishing.
"""

from .message_handler import MessageQueueWorker

__all__ = ['MessageQueueWorker']

