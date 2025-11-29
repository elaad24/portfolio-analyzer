"""
Message queue handler for Redis Streams integration.

Handles message consumption, processing, and result publishing.
Separated from main entry point for better testability and reusability.
"""

import json
import logging
import time
from typing import Optional, Dict, Any

import redis

from ..config import get_config
from ..orchestrator import PortfolioParser
from ..schemas import ParsedJobResult

logger = logging.getLogger(__name__)


class MessageQueueWorker:
    """
    Worker that consumes messages from Redis Streams and processes portfolio files.
    
    Implements the message queue integration:
    - Connects to Redis
    - Joins consumer group
    - Filters for messages with step="parse"
    - Processes files
    - Publishes results
    """
    
    def __init__(self, config=None):
        """
        Initialize worker with configuration.
        
        Args:
            config: Optional Config instance. If None, uses get_config().
        """
        if config is None:
            config = get_config()
        
        self.config = config
        
        # Redis configuration from config
        self.redis_url = config.redis_url
        self.stream_key = config.stream_key
        self.consumer_group = config.consumer_group
        self.consumer_name = config.consumer_name
        self.block_time = config.block_time
        self.count = config.message_count
        
        # Initialize Redis client
        self.redis_client: Optional[redis.Redis] = None
        
        logger.info(f"Worker initialized: {self.consumer_name}")
        logger.info(f"Redis URL: {self.redis_url}")
        logger.info(f"Stream key: {self.stream_key}")
        logger.info(f"Consumer group: {self.consumer_group}")
    
    def connect(self):
        """Connect to Redis and create consumer group if needed."""
        try:
            # Parse Redis URL
            if self.redis_url.startswith(('redis://', 'rediss://')):
                # Extract connection details
                self.redis_client = redis.from_url(
                    self.redis_url,
                    decode_responses=True  # Automatically decode responses to strings
                )
            else:
                # Fallback to default connection
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    decode_responses=True
                )
            
            # Test connection
            self.redis_client.ping()
            logger.info("✅ Connected to Redis")
            
            # Create consumer group if it doesn't exist
            try:
                self.redis_client.xgroup_create(
                    name=self.stream_key,
                    groupname=self.consumer_group,
                    id='0',  # Start from beginning
                    mkstream=True  # Create stream if it doesn't exist
                )
                logger.info(f"✅ Created consumer group: {self.consumer_group}")
            except redis.ResponseError as e:
                if 'BUSYGROUP' in str(e):
                    logger.info(f"ℹ️  Consumer group '{self.consumer_group}' already exists")
                else:
                    raise
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    def parse_message(self, message_data: Dict[str, str]) -> Optional[Dict[str, Any]]:
        """
        Parse a Redis Stream message into a JobMessage dictionary.
        
        Redis Streams store messages as key-value pairs, so we need to
        reconstruct the JSON object from the flat key-value structure.
        
        Args:
            message_data: Dictionary from Redis Stream (key-value pairs)
            
        Returns:
            Parsed message dictionary or None if invalid
        """
        try:
            # Redis Streams store messages as alternating key-value pairs
            # We need to reconstruct the JSON object
            message = {}
            
            # Handle both formats: dict with keys, or list of alternating key-value pairs
            if isinstance(message_data, dict):
                # Already a dict
                message = message_data
            elif isinstance(message_data, list):
                # List of alternating key-value pairs: [key1, val1, key2, val2, ...]
                for i in range(0, len(message_data), 2):
                    if i + 1 < len(message_data):
                        key = message_data[i]
                        value = message_data[i + 1]
                        message[key] = value
            
            # Parse JSON fields if they're strings
            for key in ['files', 'metadata']:
                if key in message and isinstance(message[key], str):
                    try:
                        message[key] = json.loads(message[key])
                    except json.JSONDecodeError:
                        pass
            
            # Convert numeric fields
            if 'timestamp' in message:
                try:
                    message['timestamp'] = int(message['timestamp'])
                except (ValueError, TypeError):
                    pass
            
            return message
            
        except Exception as e:
            logger.error(f"Failed to parse message: {e}")
            return None
    
    def should_process_message(self, message: Dict[str, Any]) -> bool:
        """
        Check if message should be processed.
        
        Only process messages where step="parse" (or "parsing").
        
        Args:
            message: Parsed message dictionary
            
        Returns:
            True if message should be processed
        """
        step = message.get('step', '').lower()
        return step in ['parse', 'parsing']
    
    def process_message(self, message_id: str, message: Dict[str, Any]) -> bool:
        """
        Process a single job message.
        
        Args:
            message_id: Redis Stream message ID
            message: Parsed message dictionary
            
        Returns:
            True if processing was successful
        """
        job_id = message.get('jobId', 'unknown')
        directory = message.get('directory', '')
        files = message.get('files', [])
        step = message.get('step', '')
        
        logger.info(f"Processing message {message_id}: jobId={job_id}, step={step}, files={len(files)}")
        
        # Validate required fields
        if not directory:
            logger.error(f"Message {message_id}: Missing 'directory' field")
            return False
        
        if not files or not isinstance(files, list):
            logger.error(f"Message {message_id}: Missing or invalid 'files' field")
            return False
        
        try:
            # Create parser and process files
            parser = PortfolioParser(job_id)
            result: ParsedJobResult = parser.parse_job(directory, files)
            
            # Convert result to dictionary for publishing
            result_dict = result.to_dict()
            
            # Publish result back to stream
            self.publish_result(job_id, result_dict)
            
            logger.info(f"✅ Successfully processed job {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process message {message_id}: {e}", exc_info=True)
            # Publish error message
            self.publish_error(job_id, str(e))
            return False
    
    def publish_result(self, job_id: str, result: Dict[str, Any]):
        """
        Publish parsing result back to the message stream.
        
        Args:
            job_id: Job identifier
            result: Parsed result dictionary
        """
        try:
            message = {
                'jobId': job_id,
                'step': 'parsing_complete',
                'status': 'done',
                'timestamp': int(time.time() * 1000),  # Unix timestamp in milliseconds
                'metadata': json.dumps(result)  # Store result in metadata
            }
            
            # Convert to Redis Stream format (flat key-value pairs)
            stream_data = {}
            for key, value in message.items():
                if isinstance(value, (dict, list)):
                    stream_data[key] = json.dumps(value)
                else:
                    stream_data[key] = str(value)
            
            # Add message to stream
            message_id = self.redis_client.xadd(
                name=self.stream_key,
                fields=stream_data
            )
            
            logger.info(f"Published result for job {job_id}: message_id={message_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish result for job {job_id}: {e}", exc_info=True)
    
    def publish_error(self, job_id: str, error_message: str):
        """
        Publish error message to the stream.
        
        Args:
            job_id: Job identifier
            error_message: Error description
        """
        try:
            message = {
                'jobId': job_id,
                'step': 'parsing',
                'status': 'error',
                'timestamp': int(time.time() * 1000),
                'error': error_message
            }
            
            # Convert to Redis Stream format
            stream_data = {}
            for key, value in message.items():
                stream_data[key] = str(value)
            
            # Add message to stream
            self.redis_client.xadd(
                name=self.stream_key,
                fields=stream_data
            )
            
            logger.info(f"Published error for job {job_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish error for job {job_id}: {e}", exc_info=True)
    
    def consume_messages(self):
        """
        Main consumption loop - reads messages from Redis Streams.
        
        This method runs continuously, blocking and waiting for new messages.
        Handles graceful shutdown on SIGTERM (for containers).
        """
        logger.info("Starting message consumption loop...")
        
        while True:
            try:
                # Read messages from stream using XREADGROUP
                # This is the Redis Streams consumer group pattern
                messages = self.redis_client.xreadgroup(
                    groupname=self.consumer_group,
                    consumername=self.consumer_name,
                    streams={self.stream_key: '>'},  # '>' means new messages only
                    count=self.count,
                    block=self.block_time  # Block for this many milliseconds
                )
                
                if not messages:
                    # No messages available, continue loop
                    continue
                
                # Process each message
                # Format: [(stream_key, [(message_id, {fields...}), ...])]
                for stream_key, message_list in messages:
                    for message_id, message_data in message_list:
                        # Parse message
                        parsed_message = self.parse_message(message_data)
                        
                        if not parsed_message:
                            logger.warning(f"Failed to parse message {message_id}, skipping")
                            continue
                        
                        # Check if we should process this message
                        if not self.should_process_message(parsed_message):
                            logger.debug(f"Skipping message {message_id}: step={parsed_message.get('step')}")
                            continue
                        
                        # Process the message
                        success = self.process_message(message_id, parsed_message)
                        
                        if success:
                            # Acknowledge message (remove from pending list)
                            try:
                                self.redis_client.xack(
                                    name=self.stream_key,
                                    groupname=self.consumer_group,
                                    *[message_id]
                                )
                                logger.debug(f"Acknowledged message {message_id}")
                            except Exception as e:
                                logger.error(f"Failed to acknowledge message {message_id}: {e}")
                        else:
                            logger.warning(f"Message {message_id} processing failed, leaving in pending")
                
            except redis.ConnectionError as e:
                logger.error(f"Redis connection error: {e}, attempting to reconnect...")
                try:
                    self.connect()
                except Exception as reconnect_error:
                    logger.error(f"Reconnection failed: {reconnect_error}")
                    # Wait before retrying
                    time.sleep(5)
            
            except KeyboardInterrupt:
                logger.info("Received interrupt signal, shutting down...")
                break
            
            except Exception as e:
                logger.error(f"Unexpected error in consumption loop: {e}", exc_info=True)
                # Continue loop even on error
                time.sleep(1)

