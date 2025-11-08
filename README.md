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
├── node-service/          # HTTP server (TypeScript + Bun)
│   ├── src/
│   │   ├── routes/       # API endpoints
│   │   ├── utils/        # Validation utilities
│   │   ├── types/        # TypeScript definitions
│   │   └── index.ts      # Entry point
│   └── tests/            # Test suite
├── python-worker/         # File parser service (Python)
│   ├── src/
│   │   ├── parsers/      # Portfolio parser
│   │   ├── ai_pipeline/  # LangChain integration (planned)
│   │   └── utils/        # Logger utilities
│   └── requirements.txt
└── project_architecture.md
```

## 🚀 Quick Start

### Prerequisites

- [Bun](https://bun.sh/) (recommended) or Node.js 18+
- Python 3.8+
- Docker (for shared storage and message queue)

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

3. **Setup Python Worker**

   ```bash
   cd python-worker
   pip install -r requirements.txt
   ```

4. **Start Node Service**
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

### 🔄 Python Worker (In Progress)

**Status**: Basic structure implemented, not yet integrated

**Features**:

- Portfolio parser using pandas
- Excel/CSV file parsing
- Data validation utilities
- Logger setup

**Pending**:

- Message queue integration
- Docker volume file access
- Integration with Node service

### ⏳ AI Pipeline (Planned)

**Status**: Not yet implemented

**Planned Features**:

- LangChain integration
- Portfolio analysis algorithms
- Key insights generation
- Result storage

### ⏳ Message Queue (Planned)

**Status**: Not yet implemented

**Planned**: Local message broker (RabbitMQ/Redis) for service orchestration

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

### Planned

- **Message Queue**: RabbitMQ or Redis
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
- 🔄 Python server (Worker)
- ⏳ LangChain agent (AI Pipeline)
- ⏳ Message broker
- ⏳ Docker integration
- ⏳ Microservices architecture
- ✅ Unit testing (Node service)

### Side Quest Goals

- ⏳ Swagger documentation
- ⏳ Rate limiting
- ⏳ Idempotency
- ⏳ Redis caching
- ⏳ Database indexing
- ⏳ Load balancing

## 📚 Development

### Environment Variables

Create `.env` in `node-service/`:

```env
PORT=3000
NODE_ENV=development
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB
MAX_FILES=10
```

### Running Services

**Node Service**:

```bash
cd node-service
bun run dev    # Development with watch mode
bun run start  # Production
```

**Python Worker**:

```bash
cd python-worker
python src/main.py
```

---

**Built with TypeScript, Python, Express.js, and Bun**
