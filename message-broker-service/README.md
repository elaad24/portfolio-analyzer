# Message Broker Service

Redis Streams-based message broker for the Portfolio Analyzer microservices architecture.

## Overview

This service provides a message queue using Redis Streams to orchestrate communication between microservices:

- **Node Service** → Publishes job messages when files are uploaded
- **Python Worker** → Consumes messages to parse files
- **AI Pipeline** → Consumes messages to analyze parsed data

## Message Schema

```typescript
{
  jobId: string;              // Unique job identifier
  directory: string;          // Directory path where files are stored
  files: string[];           // Array of file names/IDs
  step: string;              // Current processing step
  status: "pending" | "processing" | "done" | "error";
  timestamp: number;         // Unix timestamp
  error?: string;            // Optional error message
  metadata?: Record<string, any>; // Optional additional data
}
```

## Installation

```bash
# Install dependencies
bun install

# Or with npm
npm install
```

## Configuration

Set environment variables:

```bash
REDIS_URL=redis://localhost:6379          # Redis connection URL
REDIS_STREAM_KEY=portfolio:jobs          # Stream key name
CONSUMER_GROUP=portfolio-workers         # Consumer group name
CONSUMER_NAME=consumer-1                 # Unique consumer name
```

## Usage

### As a Library (in other services)

```typescript
import {
  MessageProducer,
  MessageConsumer,
  JobMessage,
} from "./message-broker-service";

// Create producer
const producer = new MessageProducer({
  streamKey: "portfolio:jobs",
  maxLength: 10000, // Optional: limit stream size
});

await producer.connect();

// Publish a message
const message: JobMessage = {
  jobId: "job-123",
  directory: "/uploads",
  files: ["file1.csv"],
  step: "file_uploaded",
  status: "pending",
  timestamp: Date.now(),
};

await producer.publish(message);

// Create consumer
const consumer = new MessageConsumer({
  streamKey: "portfolio:jobs",
  groupName: "portfolio-workers",
  consumerName: "python-worker-1",
  blockTime: 1000,
  count: 10,
});

await consumer.connect();

// Consume messages
await consumer.start(async (streamMessage) => {
  const { id, message } = streamMessage;
  console.log("Processing:", message);

  // Your processing logic here

  // Acknowledge after successful processing
  await consumer.ack(id);
}, false);
```

### As a Standalone Service

```bash
# Run the service
bun run src/index.ts

# Or in dev mode with watch
bun run dev
```

## API Reference

### MessageProducer

**Methods:**

- `connect()` - Connect to Redis
- `publish(message: JobMessage)` - Publish a single message
- `publishBatch(messages: JobMessage[])` - Publish multiple messages
- `getStreamInfo()` - Get stream information
- `getStreamLength()` - Get number of messages in stream

### MessageConsumer

**Methods:**

- `connect()` - Connect to Redis and create consumer group
- `consume(callback, autoAck)` - Read and process messages once
- `start(callback, autoAck)` - Start continuous message consumption
- `ack(messageId)` - Acknowledge a processed message
- `getPendingMessages()` - Get unacknowledged messages
- `claimPendingMessages(minIdleTime)` - Claim idle pending messages

## Job Steps

Recommended step values:

- `file_uploaded` - File successfully uploaded
- `parsing` - File parsing in progress
- `parsing_complete` - File parsing completed
- `ai_analysis` - AI analysis in progress
- `ai_analysis_complete` - AI analysis completed
- `completed` - Entire job completed

## Error Handling

Messages with `status: "error"` should include an `error` field with details. Failed messages remain in the pending list and can be recovered using `claimPendingMessages()`.

## Development

```bash
# Type check
bun run build

# Run tests (when implemented)
bun test
```

## Dependencies

- `ioredis` - Redis client for Node.js
- `uuid` - Generate unique IDs
- `typescript` - Type safety
