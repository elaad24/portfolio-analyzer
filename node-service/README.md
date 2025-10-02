# Portfolio Analyzer - File Upload Service

A robust Node.js service for handling file uploads in the Portfolio Analyzer application. This service provides secure, validated file upload capabilities for CSV and Excel files with comprehensive testing and error handling.

## 🚀 Features

- **Multiple File Upload**: Support for uploading multiple files simultaneously
- **File Type Validation**: Strict validation for CSV and XLSX files
- **File Size Limits**: Configurable file size restrictions (default: 10MB)
- **Unique File Naming**: UUID-based file naming to prevent conflicts
- **Comprehensive Testing**: 35 tests with 100% pass rate
- **TypeScript Support**: Full type safety with custom interfaces
- **Error Handling**: Detailed error responses for various failure scenarios

## 📁 Project Structure

```
node-service/
├── src/
│   ├── routes/
│   │   ├── file-handler.ts      # File upload endpoints
│   │   └── index.ts             # Route configuration
│   ├── utils/
│   │   └── fileValidation.ts    # File validation utilities
│   ├── types/
│   │   └── index.ts             # TypeScript type definitions
│   └── index.ts                 # Main application entry point
├── tests/
│   ├── routes/
│   │   └── file-handler.test.ts # Integration tests
│   ├── utils/
│   │   └── fileValidation.test.ts # Unit tests
│   ├── helpers/
│   │   └── mockFiles.ts         # Test helper functions
│   └── setup.ts                 # Test configuration
├── uploads/                     # Directory for uploaded files
├── package.json
├── jest.config.js
└── README.md
```

## 🛠️ Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd portfolio-analyzer/node-service
   ```

2. **Install dependencies**

   ```bash
   bun install
   ```

3. **Start the development server**
   ```bash
   bun run dev
   ```

## 📋 API Endpoints

### POST `/api/files/upload`

Upload one or more CSV/XLSX files for portfolio analysis.

**Request:**

- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Field Name**: `files` (can be multiple files)
- **File Types**: `.csv`, `.xlsx`, `.xls`
- **Max File Size**: 10MB per file
- **Max Files**: 10 files per request

**Example using curl:**

```bash
curl -X POST http://localhost:3000/api/files/upload \
  -F "files=@portfolio1.csv" \
  -F "files=@portfolio2.xlsx"
```

**Success Response (200):**

```json
{
  "message": "Processed 2 files",
  "successCount": 2,
  "errorCount": 0,
  "uploadedFiles": [
    {
      "originalName": "portfolio1.csv",
      "savedName": "a1b2c3d4-e5f6-7890-abcd-ef1234567890-portfolio1.csv",
      "size": 1024,
      "mimetype": "text/csv",
      "extension": ".csv",
      "path": "/path/to/uploads/a1b2c3d4-e5f6-7890-abcd-ef1234567890-portfolio1.csv"
    }
  ],
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

**Error Response (400/500):**

```json
{
  "error": "Invalid file type",
  "message": "Only CSV and XLSX files are allowed",
  "timestamp": "2024-01-15T10:30:00.000Z"
}
```

### GET `/api/files/download/:filename`

Download a previously uploaded file.

**Request:**

- **Method**: `GET`
- **Parameter**: `filename` (the saved filename with UUID)

### GET `/api/files/list`

List all uploaded files.

**Request:**

- **Method**: `GET`

## 🔧 Configuration

### File Validation Settings

Edit `src/utils/fileValidation.ts` to modify validation rules:

```typescript
// Allowed file types
export const ALLOWED_MIME_TYPES = [
  "text/csv",
  "application/vnd.ms-excel",
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
];

// Allowed file extensions
export const ALLOWED_EXTENSIONS = [".csv", ".xlsx", ".xls"];

// Maximum file size (10MB)
export const MAX_FILE_SIZE = 10 * 1024 * 1024;
```

### Multer Configuration

The service uses Multer for file handling with the following settings:

- **Storage**: Memory storage (files processed in memory)
- **File Filter**: Custom validation for file types
- **Size Limit**: 20MB (allows large files through for validation)

## 🧪 Testing

### Running Tests

```bash
# Run all tests
bun test

# Run tests in watch mode
bun run test:watch

# Run tests with coverage
bun run test:coverage

# Run specific test file
bun test tests/utils/fileValidation.test.ts
```

### Test Coverage

- **Unit Tests**: 24 tests for validation utilities
- **Integration Tests**: 11 tests for API endpoints
- **Coverage**: 100% pass rate across all scenarios

### Test Categories

1. **File Validation Tests**

   - MIME type validation
   - File extension handling
   - File size validation
   - Edge cases (empty files, uppercase extensions)

2. **Upload Endpoint Tests**
   - Single file uploads
   - Multiple file uploads
   - Error handling
   - File system operations

## 🔒 Security Features

- **File Type Validation**: Strict checking of MIME types and extensions
- **File Size Limits**: Prevents oversized file uploads
- **Unique Naming**: UUID-based filenames prevent conflicts and guessing
- **Input Sanitization**: Proper handling of file metadata
- **Error Handling**: No sensitive information leaked in error messages

## 📝 File Validation Logic

The service uses a two-tier validation approach:

1. **MIME Type Check**: Validates the file's MIME type
2. **Extension Check**: Validates the file extension as a fallback

A file is accepted if **either** the MIME type **or** the extension is valid. This approach handles cases where:

- Browsers send incorrect MIME types
- Files have missing or incorrect extensions
- Files are uploaded from different systems

## 🚨 Error Handling

The service handles various error scenarios:

- **No files uploaded**: Returns 400 with clear message
- **Invalid file types**: Returns detailed error for each rejected file
- **File too large**: Returns size limit error
- **Server errors**: Returns 500 with generic error message
- **Mixed results**: Returns success count and error details

## 🔄 Development

### Adding New File Types

1. Update `ALLOWED_MIME_TYPES` in `fileValidation.ts`
2. Update `ALLOWED_EXTENSIONS` in `fileValidation.ts`
3. Add corresponding tests
4. Update documentation

### Adding New Validation Rules

1. Create new validation function in `fileValidation.ts`
2. Add unit tests for the new function
3. Integrate into the upload endpoint
4. Add integration tests

## 📊 Performance

- **Memory Usage**: Files processed in memory for validation
- **File Size**: Supports files up to 10MB
- **Concurrent Uploads**: Handles multiple files simultaneously
- **Response Time**: Fast validation and file processing

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

This project is part of the Portfolio Analyzer application.

## 🆘 Troubleshooting

### Common Issues

1. **File Upload Fails**

   - Check file type (must be CSV or XLSX)
   - Verify file size (must be under 10MB)
   - Ensure proper form field name (`files`)

2. **Tests Failing**

   - Run `bun install` to ensure dependencies are installed
   - Check that uploads directory exists
   - Verify Jest configuration

3. **Server Errors**
   - Check file permissions for uploads directory
   - Verify available disk space
   - Check server logs for detailed error messages

### Getting Help

- Check the test files for usage examples
- Review the validation utilities for configuration options
- Examine the API responses for error details
