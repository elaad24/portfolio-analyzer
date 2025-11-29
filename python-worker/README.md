# Python Worker Service

Portfolio file parser and data normalizer for the Portfolio Analyzer microservices architecture.

## 🎯 Purpose

This worker receives job messages from the message queue, parses CSV/XLSX portfolio files, extracts all transactions, organizes them into clean categories, sorts everything by date, merges data from multiple files, and outputs a single unified internal schema.

**Important**: This worker is the **data normalizer**, not the analyzer. It prepares clean, structured data for downstream processing.

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd python-worker
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
export REDIS_URL=redis://localhost:6379
export REDIS_STREAM_KEY=portfolio:jobs
export CONSUMER_GROUP=portfolio-workers
export CONSUMER_NAME=python-worker-1
```

Or create a `.env` file (requires `python-dotenv` package):

```bash
REDIS_URL=redis://localhost:6379
REDIS_STREAM_KEY=portfolio:jobs
CONSUMER_GROUP=portfolio-workers
CONSUMER_NAME=python-worker-1
LOG_LEVEL=INFO
LOG_FILE=python-worker.log  # Optional
```

### 3. Run the Worker

```bash
python src/main.py
```

The worker will:
- Connect to Redis
- Join the consumer group
- Start listening for messages with `step="parse"`
- Process files and publish results

## 📥 Input Message Schema

The worker consumes messages from the Redis Streams message queue with the following structure:

```json
{
  "jobId": "string", // Unique job identifier for tracking
  "directory": "string", // Directory path where files are stored
  "files": ["file1.csv", "file2.xlsx"], // Array of file names/IDs to process
  "step": "parse", // Must be "parse" to trigger parsing logic
  "status": "pending", // Job status
  "timestamp": 1234567890, // Unix timestamp
  "error": null, // Optional error message
  "metadata": {} // Optional additional data
}
```

### Critical Fields

- **`directory`** → Where the files are physically stored (e.g., `/uploads`, Docker volume path)
- **`files[]`** → List of file names/IDs to load and process
- **`jobId`** → Used for tracking, correlation, and output identification
- **`step="parse"`** → Ensures the worker executes parsing logic (filter messages)

## 📄 Processing Workflow

### Step 1: Safely Open CSV/XLSX Files

**Requirements**:

- Handle corrupted files gracefully (don't crash on bad files)
- Detect file type automatically (CSV vs Excel)
- Ensure proper encoding handling (UTF-8, handle BOM if present)
- Add errors to the output array if something fails
- Continue processing other files even if one fails

**Implementation Notes**:

- Use `pandas.read_csv()` for CSV files with encoding detection
- Use `pandas.read_excel()` for XLSX files
- Wrap file operations in try-except blocks
- Log errors with file name and error details
- Add structured error objects to the `errors[]` array

### Step 2: Parse Each File and Categorize Rows

The worker must group transactions into these categories:

#### Category Definitions

1. **Purchases** (`purchases`)

   - Rows representing stock/asset purchases
   - Typically identified by transaction type or description

2. **Sales** (`sales`)

   - Rows representing stock/asset sales
   - Typically identified by transaction type or description

3. **Dividends** (`dividends`)

   - **Logic**: Any row that contains the word "dividend" (case-insensitive)
   - Extract company name from the next column (or specified column)
   - Include dividend amount and date

4. **Tax Withholding** (`taxes`)

   - **Logic**: Contains keywords like "tax", "withholding" (case-insensitive)
   - Extract tax amount and date
   - Note: Output field name is `taxes` (not `tax_withholding`)

5. **Deposits** (`transfers`)

   - Cash deposits into the account
   - Combined with Cash Handling Fee into single `transfers` array

6. **Cash Handling Fee** (`transfers`)
   - Transaction fees
   - Combined with Deposits into single `transfers` array

### Step 3: Convert Each Row into Strict Object Schema

Each categorized transaction must be converted to this standardized structure:

```python
{
  "date": "YYYY-MM-DD",           # Based on column A (or date column)
  "company_symbol": "string",     # Column D (or symbol column)
  "quantity": float,               # Column E (or quantity column)
  "unit_price": float,             # Column F (or price column)
  "currency": "string",            # Column G (or currency column)
  "transaction_fee": float,        # Column H (or fee column)
  "proceeds_foreign": float,       # Column J (or foreign proceeds)
  "proceeds_ils": float            # Column K (or ILS proceeds)
}
```

**Column Mapping Notes**:

- Column mapping will be defined during implementation
- This schema is the expected output format
- Handle missing columns gracefully (use None/null for missing values)
- Validate data types (dates, numbers, strings)

### Step 4: Sort Each Group by Date

Before finishing each file's processing:

- For each internal array (`purchases`, `sales`, `dividends`, `taxes`, `transfers`)
- Sort by `date` field in **ascending order** (oldest first)
- This ensures chronological order within each file

### Step 5: Process All Files One by One

For each file in the `files[]` array:

1. **Parse** → Open and read the file
2. **Categorize** → Group rows into transaction types
3. **Convert** → Transform rows to standardized schema
4. **Sort** → Sort each category array by date
5. **Accumulate** → Add to a global accumulating object

**Processing Strategy**:

- Process files sequentially (one at a time)
- Maintain a global accumulator object that merges all files
- Continue processing even if individual files fail (add to errors)

### Step 6: Merge Multiple Files into One Unified Dataset

After processing all files, merge them into a single chronological dataset:

**Merging Logic**:

1. **Compare timestamps** between the accumulated data and new file data:

   - If the entire file contains **newer data** than what's already stored → **append to the end**
   - If the file contains **older data** → **insert at the beginning**

2. **Optimization**: Only check this once per array (because each file is internally sorted)

3. **Result**: The final dataset is fully chronological across all files

**Example**:

```
File 1: [2023-01-01, 2023-02-01, 2023-03-01]
File 2: [2022-12-01, 2023-01-15]
Result: [2022-12-01, 2023-01-01, 2023-01-15, 2023-02-01, 2023-03-01]
```

## 📤 Output Schema

The worker returns a fully clean, normalized object:

```python
{
  "jobId": "abc123",              # Original job ID from input
  "purchases": [                  # Array of purchase transactions
    {
      "date": "2023-01-15",
      "company_symbol": "AAPL",
      "quantity": 10.0,
      "unit_price": 150.50,
      "currency": "USD",
      "transaction_fee": 1.00,
      "proceeds_foreign": 1505.00,
      "proceeds_ils": 5500.00
    },
    // ... more purchases
  ],
  "sales": [                      # Array of sale transactions
    // ... same schema as purchases
  ],
  "dividends": [                   # Array of dividend transactions
    {
      "date": "2023-02-01",
      "company_symbol": "AAPL",
      "quantity": null,            # May not apply to dividends
      "unit_price": null,
      "currency": "USD",
      "transaction_fee": 0.0,
      "proceeds_foreign": 25.00,
      "proceeds_ils": 91.25
    },
    // ... more dividends
  ],
  "taxes": [                       # Array of tax withholding transactions
    // ... same schema
  ],
  "transfers": [                   # Array of deposits and fees
    // ... same schema
  ],
  "errors": [                      # Array of error objects
    {
      "file": "corrupted_file.csv",
      "error": "File encoding error: invalid UTF-8",
      "type": "encoding_error"
    },
    {
      "file": "missing_columns.xlsx",
      "error": "Missing required column: 'date'",
      "type": "validation_error"
    }
    // ... more errors
  ]
}
```

### Output Field Notes

- **`taxes`** → Contains tax withholding transactions (not `tax_withholding`)
- **`transfers`** → Contains both deposits and cash handling fees (combined)
- **`errors[]`** → Contains warnings and errors:
  - Bad rows (invalid data)
  - Corrupted files
  - Missing columns
  - Encoding issues
  - Any other processing failures

## 🔄 Message Queue Integration

### Consuming Messages

The worker must:

1. Connect to Redis Streams using the message broker service
2. Join consumer group: `portfolio-workers`
3. Use unique consumer name (e.g., `python-worker-1`)
4. Filter for messages where `step="parse"`
5. Process messages and acknowledge after successful completion

### Publishing Results

After processing, the worker should:

1. Publish a new message with:

   - Same `jobId`
   - `step="parsing_complete"`
   - `status="done"`
   - `metadata` containing the parsed data (or reference to stored data)

2. Or update the existing message status

## 🏗️ Code Structure

The worker follows a modular architecture with clear separation of concerns:

```
python-worker/
├── README.md
├── requirements.txt
├── src/
│   ├── __init__.py             # Package exports
│   ├── main.py                 # Entry point (minimal bootstrap)
│   ├── config.py               # Configuration management
│   ├── orchestrator.py         # Main parsing pipeline orchestration
│   ├── queue/
│   │   ├── __init__.py
│   │   └── message_handler.py  # Redis Streams integration
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── file_loader.py      # File loading and validation
│   │   ├── csv_parser.py       # CSV-specific parsing logic
│   │   └── excel_parser.py     # Excel-specific parsing logic
│   ├── processors/
│   │   ├── __init__.py
│   │   ├── categorizer.py      # Transaction categorization
│   │   ├── transformer.py      # Row-to-schema transformation
│   │   └── merger.py            # Multi-file chronological merging
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── models.py           # Data models (dataclasses)
│   └── utils/
│       ├── __init__.py
│       ├── date_utils.py        # Date parsing utilities
│       └── number_utils.py     # Number parsing utilities
└── tests/
    ├── __init__.py
    ├── test_orchestrator.py    # Orchestrator tests
    └── test_merger.py          # Merger tests
```

### Architecture Rationale

**Why this structure?**

1. **Separation of Concerns**: Each module has a single, clear responsibility

   - `parsers/` - File I/O and parsing
   - `processors/` - Business logic (categorization, transformation, merging)
   - `schemas/` - Data models
   - `queue/` - Infrastructure (Redis/message queue)
   - `config.py` - Configuration management

2. **Scalability**: Easy to add new parsers, processors, or schemas without touching existing code

3. **Testability**: Clear boundaries make unit testing straightforward

4. **Container-Ready**: Configuration via environment variables, graceful shutdown handling

5. **Maintainability**: Related code is grouped together, making navigation intuitive

## 📋 Implementation Checklist

### Core Functionality

- [ ] Message queue consumer setup (Redis Streams)
- [ ] File type detection (CSV vs Excel)
- [ ] Safe file opening with error handling
- [ ] Transaction categorization logic
- [ ] Schema transformation (row → standard object)
- [ ] Date sorting within each category
- [ ] Multi-file merging with chronological ordering
- [ ] Error collection and reporting

### Data Processing

- [ ] CSV parser with encoding detection
- [ ] Excel parser (XLSX support)
- [ ] Column mapping configuration
- [ ] Data type validation
- [ ] Date parsing and normalization
- [ ] Missing value handling

### Error Handling

- [ ] Corrupted file handling
- [ ] Missing column detection
- [ ] Invalid data type handling
- [ ] Encoding error recovery
- [ ] Structured error reporting

### Integration

- [ ] Redis connection and consumer group setup
- [ ] Message filtering (`step="parse"`)
- [ ] Message acknowledgment
- [ ] Result publishing to message queue
- [ ] Docker volume file access

## 🔧 Configuration

Configuration is managed through environment variables, making it easy to configure for different environments (development, staging, production) and containerized deployments.

### Environment Variables

```bash
# Redis Connection
REDIS_URL=redis://localhost:6379
REDIS_STREAM_KEY=portfolio:jobs
CONSUMER_GROUP=portfolio-workers
CONSUMER_NAME=python-worker-1
BLOCK_TIME=1000                        # Milliseconds to block waiting for messages
MESSAGE_COUNT=10                       # Max messages per read

# Logging
LOG_LEVEL=INFO                         # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE=python-worker.log             # Optional: set to enable file logging
```

**Note**: All configuration is centralized in `src/config.py` using the `Config` class. The configuration is validated on startup and logging is automatically configured.

## 🧪 Testing

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_orchestrator.py

# Run with verbose output
python -m pytest tests/ -v
```

### Testing Without Message Queue

You can test the parser directly without Redis:

```python
from src.orchestrator import PortfolioParser

# Create parser
parser = PortfolioParser("test-job-123")

# Process files
result = parser.parse_job(
    directory="/path/to/files",
    files=["file1.csv", "file2.xlsx"]
)

# Get result as dictionary
result_dict = result.to_dict()
print(result_dict)
```

### Testing Strategy

**Unit Tests**:
- File parser tests (CSV, Excel)
- Categorization logic tests
- Schema transformation tests
- Date sorting tests
- File merging logic tests

**Integration Tests**:
- Message queue consumption
- End-to-end file processing
- Error handling scenarios
- Multi-file processing

**Test Data**:
- Sample CSV files (various formats)
- Sample Excel files
- Corrupted files (for error handling)
- Files with missing columns
- Files with invalid data types

## 📝 Code Quality Guidelines

### Code Style

- Follow PEP 8 Python style guide
- Use type hints for function signatures
- Add docstrings to all functions and classes
- Keep functions small and focused (single responsibility)

### Comments

- Add comments for complex logic
- Explain business rules (e.g., categorization rules)
- Document column mappings
- Clarify merging algorithm

### Error Handling

- Use specific exception types
- Provide meaningful error messages
- Log errors with context (file name, row number, etc.)
- Never crash on a single file error

### Performance

- Process files efficiently (use pandas vectorization)
- Avoid loading entire files into memory if not needed
- Optimize date sorting (use pandas sort_values)
- Consider streaming for very large files

## 🔍 Example Processing Flow

```
1. Receive message:
   {
     "jobId": "job-123",
     "directory": "/uploads",
     "files": ["file1.csv", "file2.xlsx"],
     "step": "parse"
   }

2. Process file1.csv:
   - Open file (detect CSV)
   - Parse rows
   - Categorize: 5 purchases, 3 sales, 2 dividends
   - Transform to schema
   - Sort by date

3. Process file2.xlsx:
   - Open file (detect Excel)
   - Parse rows
   - Categorize: 2 purchases, 1 sale
   - Transform to schema
   - Sort by date

4. Merge files:
   - Compare timestamps
   - Merge purchases chronologically
   - Merge sales chronologically
   - Merge dividends chronologically
   - etc.

5. Output:
   {
     "jobId": "job-123",
     "purchases": [...merged, sorted...],
     "sales": [...merged, sorted...],
     "dividends": [...merged, sorted...],
     "taxes": [...],
     "transfers": [...],
     "errors": []
   }

6. Publish result message to queue
```

**Note**: This worker is a critical component in the data pipeline. It must be robust, handle errors gracefully, and produce clean, normalized data for downstream analysis.

## 🔧 Troubleshooting

### Redis Connection Error

```
Failed to connect to Redis: ...
```

**Solution**: Make sure Redis is running:

```bash
redis-server
# Or with Docker:
docker run -d -p 6379:6379 redis:latest
```

### File Not Found

```
File not found: filename.csv
```

**Solution**: Check that:
- The `directory` path in the message is correct
- Files exist in that directory
- The worker has read permissions

### Import Errors

```
ModuleNotFoundError: No module named 'schemas'
```

**Solution**: Make sure you're running from the correct directory:

```bash
cd python-worker
python src/main.py
```

Or add the src directory to PYTHONPATH:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
python src/main.py
```

## 🛠️ Development

### Adding New Transaction Types

1. Add keyword to `processors/categorizer.py`
2. Add transformation function to `processors/transformer.py`
3. Add schema class to `schemas/models.py`
4. Update `orchestrator.py` to handle new category

### Adding New File Formats

1. Create new parser in `parsers/` (e.g., `parsers/json_parser.py`)
2. Update `parsers/file_loader.py` to detect and delegate to new parser
3. Export new parser in `parsers/__init__.py`
