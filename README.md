# Portfolio Analyzer

A comprehensive portfolio analysis application that helps users analyze their investment portfolios through file uploads and data processing. The application consists of a Node.js backend service for file handling and validation.

## 🏗️ Project Architecture

```
portfolio-analyzer/
├── node-service/           # Backend file upload service
│   ├── src/               # Source code
│   ├── tests/             # Test suite
│   ├── uploads/           # Uploaded files storage
│   └── README.md          # Service-specific documentation
└── README.md              # This file
```

## 🚀 Quick Start

### Prerequisites

- [Bun](https://bun.sh/) (recommended) or Node.js 18+
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd portfolio-analyzer
   ```

2. **Install dependencies**

   ```bash
   cd node-service
   bun install
   ```

3. **Start the development server**
   ```bash
   bun run dev
   ```

The service will be available at `http://localhost:3000`

## 📋 Services

### Node Service - File Upload & Validation

The core backend service that handles file uploads and validation for portfolio data.

**Location**: `./node-service/`

**Key Features**:

- ✅ **Multiple File Upload**: Support for CSV and XLSX files
- ✅ **File Validation**: Strict type and size validation
- ✅ **Secure Storage**: UUID-based file naming
- ✅ **Comprehensive Testing**: 35 tests with 100% pass rate
- ✅ **TypeScript Support**: Full type safety
- ✅ **Error Handling**: Detailed error responses

**API Endpoints**:

- `POST /api/files/upload` - Upload portfolio files
- `GET /api/files/download/:filename` - Download files
- `GET /api/files/list` - List uploaded files

**Supported File Types**:

- CSV files (`.csv`)
- Excel files (`.xlsx`, `.xls`)
- Maximum file size: 10MB per file
- Maximum files per request: 10

**Example Usage**:

```bash
# Upload a portfolio file
curl -X POST http://localhost:3000/api/files/upload \
  -F "files=@portfolio.csv"
```

**Response**:

```json
{
  "message": "Processed 1 files",
  "successCount": 1,
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

For detailed documentation, see [node-service/README.md](./node-service/README.md)

## 🧪 Testing

### Running Tests

```bash
cd node-service
bun test                    # Run all tests
bun run test:watch         # Run tests in watch mode
bun run test:coverage      # Run tests with coverage
```

### Test Coverage

- **Unit Tests**: 24 tests for validation utilities
- **Integration Tests**: 11 tests for API endpoints
- **Total Coverage**: 35 tests with 100% pass rate

## 🔧 Development

### Project Structure

```
portfolio-analyzer/
├── node-service/              # Backend service
│   ├── src/
│   │   ├── routes/           # API route handlers
│   │   ├── utils/            # Utility functions
│   │   ├── types/            # TypeScript definitions
│   │   └── index.ts          # Application entry point
│   ├── tests/                # Test suite
│   │   ├── routes/           # Integration tests
│   │   ├── utils/            # Unit tests
│   │   ├── helpers/          # Test utilities
│   │   └── setup.ts          # Test configuration
│   ├── uploads/              # File storage
│   ├── package.json          # Dependencies
│   ├── jest.config.js        # Test configuration
│   └── README.md             # Service documentation
└── README.md                 # Project overview
```

### Technology Stack

- **Runtime**: Bun (with Node.js compatibility)
- **Language**: TypeScript
- **Framework**: Express.js
- **File Handling**: Multer
- **Testing**: Jest + Supertest
- **Validation**: Custom validation utilities

### Key Dependencies

```json
{
  "dependencies": {
    "express": "^5.1.0",
    "multer": "^1.4.5-lts.1",
    "uuid": "^13.0.0"
  },
  "devDependencies": {
    "jest": "^30.2.0",
    "supertest": "^7.1.4",
    "typescript": "^5.9.3"
  }
}
```

## 🔒 Security Features

- **File Type Validation**: Strict MIME type and extension checking
- **File Size Limits**: Configurable size restrictions
- **Unique File Naming**: UUID-based naming prevents conflicts
- **Input Sanitization**: Proper handling of file metadata
- **Error Handling**: No sensitive information in error messages

## 📊 Performance

- **Memory Efficient**: Files processed in memory for validation
- **Scalable**: Handles multiple concurrent uploads
- **Fast Validation**: Optimized file type checking
- **Configurable Limits**: Adjustable file size and count limits

## 🚀 Deployment

### Development

```bash
cd node-service
bun run dev
```

### Production

```bash
cd node-service
bun run start
```

### Environment Variables

Create a `.env` file in the `node-service` directory:

```env
PORT=3000
NODE_ENV=production
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB in bytes
MAX_FILES=10
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass (`bun test`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Development Guidelines

- Write tests for all new functionality
- Follow TypeScript best practices
- Use conventional commit messages
- Update documentation for API changes
- Ensure 100% test coverage

## 📝 API Documentation

### File Upload Service

The node-service provides a RESTful API for file uploads:

| Method | Endpoint                        | Description             |
| ------ | ------------------------------- | ----------------------- |
| POST   | `/api/files/upload`             | Upload CSV/XLSX files   |
| GET    | `/api/files/download/:filename` | Download uploaded file  |
| GET    | `/api/files/list`               | List all uploaded files |

### Request/Response Examples

**Upload Files**:

```bash
curl -X POST http://localhost:3000/api/files/upload \
  -F "files=@portfolio1.csv" \
  -F "files=@portfolio2.xlsx"
```

**Download File**:

```bash
curl -X GET http://localhost:3000/api/files/download/uuid-filename.csv
```

**List Files**:

```bash
curl -X GET http://localhost:3000/api/files/list
```

## 🆘 Troubleshooting

### Common Issues

1. **Service Won't Start**

   - Check if port 3000 is available
   - Verify all dependencies are installed (`bun install`)
   - Check for TypeScript compilation errors

2. **File Upload Fails**

   - Verify file type (CSV or XLSX only)
   - Check file size (under 10MB)
   - Ensure proper form field name (`files`)

3. **Tests Failing**
   - Run `bun install` to update dependencies
   - Check that uploads directory exists
   - Verify Jest configuration

### Getting Help

- Check the [node-service README](./node-service/README.md) for detailed documentation
- Review test files for usage examples
- Check server logs for detailed error messages
- Open an issue for bugs or feature requests

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🗺️ Roadmap

### Planned Features

- [ ] **Data Processing**: Portfolio analysis algorithms
- [ ] **Database Integration**: Persistent storage for portfolio data
- [ ] **User Authentication**: Secure user management
- [ ] **Frontend Interface**: Web-based file upload interface
- [ ] **API Documentation**: Interactive API documentation
- [ ] **Docker Support**: Containerized deployment
- [ ] **CI/CD Pipeline**: Automated testing and deployment

### Current Status

- ✅ **File Upload Service**: Complete with full testing
- ✅ **File Validation**: Comprehensive validation system
- ✅ **Error Handling**: Robust error management
- ✅ **Documentation**: Complete API and setup documentation
- 🔄 **Data Processing**: In development
- ⏳ **Frontend Interface**: Planned

## 📞 Support

For support, questions, or contributions:

- Open an issue on GitHub
- Check the documentation in `node-service/README.md`
- Review the test files for usage examples

---

**Built with ❤️ using TypeScript, Express.js, and Bun**
