# Portfolio Analyzer

An event-based microservices application for analyzing investment portfolios through file uploads, data parsing, and AI-powered analysis.

## 🏗️ Architecture

The system consists of 4 microservices communicating through a message queue:

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│ Node Service│ ───> │ Message Queue│ ───> │Python Worker│ ───> │ AI Pipeline  │
│ (HTTP API)  │      │   (Broker)   │      │  (Parser)   │      │ (LangChain)  │
└─────────────┘      └──────────────┘      └─────────────┘      └──────────────┘
       │                     │                     │                     │
       └─────────────────────┴─────────────────────┴─────────────────────┘
                              │
                        ┌─────▼─────┐
                        │  Docker   │
                        │  Volume   │
                        │ (Storage) │
                        └───────────┘
```

### Data Flow

1. **File Upload** → User uploads portfolio files (CSV/XLSX) via REST API
2. **Storage** → Files stored in Docker volume with unique file IDs
3. **Message Queue** → Node service publishes file IDs to message broker
4. **Python Worker** → Consumes messages, parses files, validates data
5. **AI Pipeline** → Processes parsed data using LangChain for analysis
6. **Results** → Analyzed data stored and accessible via API

## 📦 Project Structure

```
portfolio-analyzer/
├── node-service/              # HTTP server (TypeScript + Bun)
│   ├── src/
│   │   ├── routes/           # API endpoints
│   │   ├── utils/            # Validation utilities
│   │   ├── types/            # TypeScript definitions
│   │   └── index.ts          # Entry point
│   └── tests/                # Test suite
├── message-broker-service/    # Redis Streams message broker (TypeScript + Bun)
│   ├── src/
│   │   ├── producer/         # Message publisher
│   │   ├── consumer/         # Message consumer
│   │   ├── utils/            # Redis connection utilities
│   │   ├── types/            # TypeScript definitions
│   │   └── index.ts          # Entry point
│   └── package.json
├── python-worker/             # File parser service (Python)
│   ├── src/
│   │   ├── main.py           # Entry point
│   │   ├── config.py         # Configuration management
│   │   ├── orchestrator.py   # Pipeline orchestration
│   │   ├── queue/            # Redis Streams integration
│   │   ├── parsers/          # File parsing (CSV, Excel)
│   │   ├── processors/       # Business logic (categorization, transformation, merging)
│   │   ├── schemas/          # Data models
│   │   └── utils/            # Utility functions
│   ├── tests/               # Test suite
│   └── requirements.txt
└── project_architecture.md
```

## 🚀 Quick Start

### Prerequisites

- [Bun](https://bun.sh/) (recommended) or Node.js 18+
- Python 3.8+
- Redis 6.0+ (for message broker)
- Docker (for shared storage, optional)

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd portfolio-analyzer
   ```

2. **Setup Node Service**

   ```bash
   cd node-service
   bun install
   ```

3. **Setup Message Broker Service**

   ```bash
   cd message-broker-service
   bun install
   ```

4. **Setup Python Worker**

   ```bash
   cd python-worker
   pip install -r requirements.txt
   ```

5. **Start Redis** (required for message broker)

   ```bash
   # Using Docker
   docker run -d -p 6379:6379 redis:latest

   # Or using local Redis installation
   redis-server
   ```

6. **Start Node Service**
   ```bash
   cd node-service
   bun run dev
   ```
   Service runs at `http://localhost:3000`

## 📋 Current Implementation Status

### ✅ Node Service (Implemented)

**Status**: Fully functional file upload service

**Features**:

- Multiple file upload (CSV, XLSX)
- File validation (type, size)
- UUID-based file naming
- Comprehensive test suite (35 tests)
- TypeScript with full type safety

**API Endpoints**:

- `POST /api/files/upload` - Upload portfolio files
- `GET /health` - Health check
- `GET /api/files/download/:filename` - Download files (placeholder)
- `GET /api/files/list` - List files (placeholder)

**File Limits**:

- Max file size: 10MB per file
- Max files per request: 10
- Supported formats: `.csv`, `.xlsx`, `.xls`

**Example Request**:

```bash
curl -X POST http://localhost:3000/api/files/upload \
  -F "files=@portfolio.csv" \
  -F "files=@portfolio2.xlsx"
```

**Response**:

```json
{
  "message": "Processed 2 files",
  "successCount": 2,
  "errorCount": 0,
  "uploadedFiles": [
    {
      "originalName": "portfolio.csv",
      "savedName": "uuid-portfolio.csv",
      "size": 1024,
      "mimetype": "text/csv",
      "extension": ".csv",
      "path": "/path/to/uploads/uuid-portfolio.csv"
    }
  ],
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### ✅ Python Worker (Implemented)

**Status**: Fully functional portfolio file parser with message queue integration

**Architecture**: Modular, container-ready architecture with clear separation of concerns:

- **`orchestrator.py`** - Main pipeline orchestration
- **`queue/`** - Redis Streams message queue integration
- **`parsers/`** - File loading and parsing (CSV, Excel)
- **`processors/`** - Business logic (categorization, transformation, merging)
- **`schemas/`** - Data models and output schemas
- **`config.py`** - Centralized configuration management

**Features**:

- ✅ Portfolio parser using pandas
- ✅ Excel/CSV file parsing with encoding detection
- ✅ Transaction categorization (purchases, sales, dividends, taxes, transfers)
- ✅ Multi-file chronological merging
- ✅ Redis Streams message queue integration
- ✅ Configuration via environment variables
- ✅ Graceful shutdown handling (container-ready)
- ✅ Comprehensive error handling and reporting
- ✅ Data validation utilities
- ✅ Logger setup (stdout + optional file logging)

**Message Queue Integration**:

- Consumes messages from Redis Streams
- Filters for `step="parse"` messages
- Processes files and publishes results
- Supports consumer groups for horizontal scaling
- Automatic message acknowledgment

**Configuration**:

All configuration via environment variables:

- `REDIS_URL` - Redis connection URL
- `REDIS_STREAM_KEY` - Stream key name
- `CONSUMER_GROUP` - Consumer group name
- `CONSUMER_NAME` - Unique consumer name
- `LOG_LEVEL` - Logging level
- `LOG_FILE` - Optional file logging path

See `python-worker/README.md` for detailed documentation.

### ⏳ AI Pipeline (Planned)

**Status**: Not yet implemented

**Planned Features**:

- LangChain integration
- Portfolio analysis algorithms
- Key insights generation
- Result storage

### ✅ Message Broker Service (Implemented)

**Status**: Fully functional Redis Streams-based message broker

**Technology**: Redis Streams with ioredis client

**Architecture Overview**:

The message broker is built using **Redis Streams**, which provides a robust, scalable message queue system. Here's how it works:

**Why Redis Streams?**

- **Consumer Groups**: Multiple workers can process messages in parallel with automatic load balancing
- **Message Persistence**: Messages are stored in Redis, ensuring no data loss
- **At-least-once Delivery**: Messages are acknowledged after processing, preventing duplicates
- **Pending Message Recovery**: Failed messages can be reclaimed and retried
- **Built-in Ordering**: Messages maintain order within the stream

**How It Was Built**:

1. **MessageProducer Class** (`src/producer/index.ts`):

   - Publishes job messages to Redis Streams using `XADD` command
   - Converts TypeScript `JobMessage` objects to Redis stream format (key-value pairs)
   - Supports batch publishing for efficiency
   - Optional `MAXLEN` parameter to limit stream size and manage memory

2. **MessageConsumer Class** (`src/consumer/index.ts`):

   - Uses consumer groups (`XREADGROUP`) to enable multiple workers
   - Each consumer has a unique name for tracking
   - Supports blocking reads (waits for new messages)
   - Automatic message acknowledgment after processing
   - Handles pending messages (unacknowledged messages can be reclaimed)

3. **Redis Connection Utility** (`src/utils/redis.ts`):

   - Singleton pattern for Redis client (one connection per service)
   - Automatic reconnection with exponential backoff
   - Connection state management

4. **Type Safety** (`src/types/index.ts`):
   - Strongly typed message schema with enums for status and steps
   - Ensures message structure consistency across services

**Key Features**:

- **Producer**: Publish single or batch messages to stream
- **Consumer**: Read messages with consumer groups for load balancing
- **Auto-acknowledgment**: Optional automatic message acknowledgment
- **Pending Recovery**: Reclaim messages from failed consumers
- **Stream Management**: Get stream info and length
- **Type Safety**: Full TypeScript support with enums and interfaces

**Message Schema**:

```typescript
{
  jobId: string;              // Unique job identifier
  directory: string;          // Directory path where files are stored
  files: string[];           // Array of file names/IDs
  step: JobStepEnum;          // Current processing step
  status: JobStatusEnum;      // "pending" | "processing" | "done" | "error"
  timestamp: number;         // Unix timestamp
  error?: string;            // Optional error message
  metadata?: Record<string, any>; // Optional additional data
}
```

**How to Use**:

**As a Library** (in other services):

```typescript
import {
  MessageProducer,
  MessageConsumer,
  JobMessage,
} from "./message-broker-service";

// Create and use producer
const producer = new MessageProducer({
  streamKey: "portfolio:jobs",
  maxLength: 10000,
});
await producer.connect();

const message: JobMessage = {
  jobId: "job-123",
  directory: "/uploads",
  files: ["file1.csv"],
  step: "file_uploaded",
  status: "pending",
  timestamp: Date.now(),
};
await producer.publish(message);

// Create and use consumer
const consumer = new MessageConsumer({
  streamKey: "portfolio:jobs",
  groupName: "portfolio-workers",
  consumerName: "python-worker-1",
  blockTime: 1000,
  count: 10,
});
await consumer.connect();

await consumer.start(async (streamMessage) => {
  console.log("Processing:", streamMessage.message);
  // Process message...
  await consumer.ack(streamMessage.id);
}, false);
```

**Configuration**:

Set environment variables:

```bash
REDIS_URL=redis://localhost:6379          # Redis connection URL
REDIS_STREAM_KEY=portfolio:jobs          # Stream key name
CONSUMER_GROUP=portfolio-workers         # Consumer group name
CONSUMER_NAME=consumer-1                 # Unique consumer name
```

**Job Steps** (workflow progression):

- `file_uploaded` → File successfully uploaded
- `parsing` → File parsing in progress
- `parsing_complete` → File parsing completed
- `ai_analysis` → AI analysis in progress
- `ai_analysis_complete` → AI analysis completed
- `completed` → Entire job completed

**Error Handling**:

- Messages with `status: "error"` include an `error` field
- Failed messages remain in pending list for recovery
- Use `claimPendingMessages()` to reclaim idle messages from failed consumers

For detailed API reference, see `message-broker-service/README.md`

## 🛠️ Technology Stack

### Node Service

- **Runtime**: Bun (with Node.js compatibility)
- **Language**: TypeScript
- **Framework**: Express.js
- **File Handling**: Multer
- **Testing**: Jest + Supertest

### Python Worker

- **Language**: Python 3.8+
- **Data Processing**: Pandas
- **Excel Support**: openpyxl
- **Message Queue**: Redis Streams (via redis-py)
- **Architecture**: Modular with clear separation of concerns
- **Container-Ready**: Environment-based configuration, graceful shutdown

### Message Broker Service

- **Runtime**: Bun (with Node.js compatibility)
- **Language**: TypeScript
- **Message Queue**: Redis Streams
- **Client Library**: ioredis
- **Features**: Consumer groups, message acknowledgment, pending recovery

### Planned

- **AI Framework**: LangChain
- **Containerization**: Docker Compose

## 🧪 Testing

### Node Service Tests

```bash
cd node-service
bun test                    # Run all tests
bun run test:watch         # Watch mode
bun run test:coverage      # Coverage report
```

**Test Coverage**:

- 24 unit tests (validation utilities)
- 11 integration tests (API endpoints)
- 100% pass rate

## 📡 API Reference

### Upload Files

**Endpoint**: `POST /api/files/upload`

**Request**:

- Content-Type: `multipart/form-data`
- Field name: `files` (array)
- Max files: 10
- Max size: 10MB per file

**Response**: `200 OK`

```json
{
  "message": "Processed N files",
  "successCount": number,
  "errorCount": number,
  "uploadedFiles": UploadedFileInfo[],
  "errors": FileUploadError[],
  "timestamp": string
}
```

### Health Check

**Endpoint**: `GET /health`

**Response**: `200 OK`

```json
{
  "status": "OK",
  "uptime": number,
  "timestamp": string
}
```

## 🔒 Security & Validation

- **File Type Validation**: Strict MIME type and extension checking
- **File Size Limits**: 10MB per file maximum
- **Unique File Naming**: UUID-based naming prevents conflicts
- **Input Sanitization**: Proper handling of file metadata
- **Error Handling**: No sensitive information in error messages

## 📝 Planned Endpoints

According to the architecture, the following endpoints are planned:

- `POST /upload` - Upload files (currently `/api/files/upload`)
- `GET /analyzedInfo/:user_uniq_number` - Retrieve analysis results by unique ID

## 🎯 Goals & Roadmap

### Main Goals

- ✅ Express server (Node service)
- ✅ Message broker (Redis Streams)
- ✅ Python server (Worker) - Fully implemented with message queue integration
- ⏳ LangChain agent (AI Pipeline)
- ⏳ Docker integration
- ✅ Microservices architecture - Event-based communication implemented
- ✅ Unit testing (Node service, Python worker)

### Side Quest Goals

- ⏳ Swagger documentation
- ⏳ Rate limiting
- ⏳ Idempotency
- ⏳ Redis caching
- ⏳ Database indexing
- ⏳ Load balancing

## 📚 Development

### Environment Variables

**Node Service** (`.env` in `node-service/`):

```env
PORT=3000
NODE_ENV=development
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB
MAX_FILES=10
```

**Message Broker Service** (`.env` in `message-broker-service/`):

```env
REDIS_URL=redis://localhost:6379
REDIS_STREAM_KEY=portfolio:jobs
CONSUMER_GROUP=portfolio-workers
CONSUMER_NAME=consumer-1
```

**Python Worker** (`.env` in `python-worker/` or environment variables):

```env
REDIS_URL=redis://localhost:6379
REDIS_STREAM_KEY=portfolio:jobs
CONSUMER_GROUP=portfolio-workers
CONSUMER_NAME=python-worker-1
BLOCK_TIME=1000                    # Milliseconds to block waiting for messages
MESSAGE_COUNT=10                    # Max messages per read
LOG_LEVEL=INFO                      # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=python-worker.log          # Optional: file logging path
```

### Running Services

**Node Service**:

```bash
cd node-service
bun run dev    # Development with watch mode
bun run start  # Production
```

**Message Broker Service**:

```bash
cd message-broker-service
bun run dev    # Development with watch mode
bun run start  # Production
```

**Python Worker**:

```bash
cd python-worker

# Set environment variables (or use .env file)
export REDIS_URL=redis://localhost:6379
export REDIS_STREAM_KEY=portfolio:jobs
export CONSUMER_GROUP=portfolio-workers
export CONSUMER_NAME=python-worker-1

# Run the worker
python src/main.py
```

The worker will:

- Connect to Redis Streams
- Join the consumer group
- Listen for messages with `step="parse"`
- Process portfolio files (CSV/XLSX)
- Publish results back to the message queue

---

**Built with TypeScript, Python, Express.js, and Bun**
