# Architecture Documentation

## Overview

InvoiceIQ is built with a modular architecture that separates concerns into distinct layers, making the application maintainable, testable, and scalable.

## System Architecture

```
┌─────────────────────────────────────────────────┐
│              User Interface Layer                │
│                 (Streamlit)                      │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────┐
│           Application Layer (app.py)             │
│  - Request Handling                              │
│  - UI Rendering                                  │
│  - Session Management                            │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────┐
│              Business Logic Layer                │
│                    (src/)                        │
├──────────────────────────────────────────────────┤
│  ┌────────────┐  ┌────────────┐  ┌────────────┐ │
│  │ OCR Module │  │ LLM Module │  │  Database  │ │
│  │  (ocr.py)  │  │  (llm.py)  │  │(database.py)│ │
│  └────────────┘  └────────────┘  └────────────┘ │
│  ┌────────────────────────────────────────────┐ │
│  │      Utilities (utils.py, logger.py)       │ │
│  └────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────┴──────────────────────────────┐
│              Infrastructure Layer                │
│  - Configuration (config.py)                     │
│  - Environment Variables (.env)                  │
│  - Database (SQLite)                             │
│  - External APIs (Google AI, Tesseract)          │
└──────────────────────────────────────────────────┘
```

## Component Details

### 1. User Interface Layer (`app.py`)

**Responsibility**: Handle user interactions and render the UI

**Key Functions**:
- `render_header()`: Display application header
- `render_upload_page()`: Invoice upload interface
- `render_search_page()`: Search and export interface
- `render_statistics()`: Dashboard metrics
- `process_invoice_file()`: Orchestrate invoice processing

**Design Patterns**:
- Session state management for component initialization
- Form-based input handling
- Progress indicators for long operations

### 2. OCR Module (`src/ocr.py`)

**Responsibility**: Extract text from PDF documents

**Class**: `OCRProcessor`

**Methods**:
- `extract_text_from_pdf(pdf_path)`: Main OCR processing
- `process_uploaded_file(file_bytes, filename)`: Handle uploaded files
- `validate_tesseract_installation()`: System check

**Dependencies**:
- Tesseract OCR
- pdf2image
- Pillow

**Error Handling**:
- File not found errors
- OCR processing failures
- Invalid file format

### 3. LLM Module (`src/llm.py`)

**Responsibility**: Extract structured data using AI

**Class**: `InvoiceExtractor`

**Methods**:
- `extract_invoice_data(invoice_text)`: Main extraction
- `_parse_llm_output(llm_output)`: Parse AI response
- `validate_api_key()`: Configuration check

**Prompt Engineering**:
- System instruction defines AI role
- Extraction prompt specifies output format
- Structured parsing with regex

**Safety**:
- Content safety filters
- Fallback for blocked responses
- Default values for failed extraction

### 4. Database Module (`src/database.py`)

**Responsibility**: Data persistence and retrieval

**Class**: `DatabaseManager`

**Methods**:
- `insert_invoice()`: Create invoice record
- `search_invoices()`: Query with filters
- `get_statistics()`: Aggregate queries
- `delete_invoice()`: Remove record

**Features**:
- Context manager for connections
- Automatic transaction management
- Indexed searches for performance
- Connection pooling via context manager

**Schema**:
```sql
CREATE TABLE invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company_name TEXT NOT NULL,
    invoice_date DATE NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
```

### 5. Utilities Module (`src/utils.py`)

**Responsibility**: Shared utility functions

**Classes**:
- `DateParser`: Multi-format date parsing
- `AmountParser`: Currency amount parsing
- `Validator`: Data validation

**Features**:
- All date formats supported
- Multiple currency formats
- Comprehensive validation rules

### 6. Logger Module (`src/logger.py`)

**Responsibility**: Centralized logging

**Features**:
- Console and file logging
- Configurable log levels
- Structured log format
- Automatic log rotation

## Data Flow

### Invoice Upload Flow

```
1. User uploads PDF
   ↓
2. File saved temporarily
   ↓
3. OCRProcessor extracts text
   ↓
4. Text sent to LLM
   ↓
5. LLM returns structured data
   ↓
6. Data displayed for review
   ↓
7. User confirms/edits
   ↓
8. Utilities validate data
   ↓
9. DatabaseManager saves record
   ↓
10. Confirmation shown to user
```

### Search Flow

```
1. User enters search criteria
   ↓
2. Criteria validated
   ↓
3. DatabaseManager queries database
   ↓
4. Results formatted as DataFrame
   ↓
5. Table displayed to user
   ↓
6. Export options available
```

## Configuration Management

**File**: `config.py`

**Environment Variables**:
- `GOOGLE_API_KEY`: AI API authentication
- `TESSERACT_CMD`: OCR executable path
- `DATABASE_PATH`: SQLite file location
- `LOG_LEVEL`: Logging verbosity
- `LLM_*`: AI model parameters

**Validation**:
- Startup configuration checks
- Missing credential detection
- Path existence verification

## Error Handling Strategy

### Layers of Error Handling

1. **Input Validation**: Early detection of invalid data
2. **Try-Catch Blocks**: Exception handling in each module
3. **Logging**: All errors logged with context
4. **User Feedback**: User-friendly error messages
5. **Fallback Values**: Sensible defaults when extraction fails

### Example Error Flow

```python
try:
    # Attempt operation
    result = risky_operation()
except SpecificError as e:
    # Log with context
    logger.error(f"Operation failed: {e}")
    # User-friendly message
    st.error("Could not process file")
    # Return safe default
    return default_value
```

## Testing Strategy

### Unit Tests
- Individual module testing
- Mocked dependencies
- Edge case coverage

### Integration Tests
- Component interaction
- Database operations
- File processing

### Test Coverage Goals
- Core modules: 80%+
- Utility functions: 90%+
- Critical paths: 100%

## Deployment Architecture

### Docker Deployment

```
┌─────────────────────────────────────┐
│         Docker Container            │
├─────────────────────────────────────┤
│  Streamlit App (Port 8501)          │
│                                     │
│  Volumes:                           │
│  - /app/data → SQLite DB            │
│  - /app/logs → Application logs     │
│  - /app/Invoices → Sample data      │
│                                     │
│  Environment:                       │
│  - API keys from .env               │
│  - Configuration settings           │
└─────────────────────────────────────┘
```

### Scalability Considerations

**Current Limitations**:
- Single SQLite database
- In-memory session state
- No distributed processing

**Future Enhancements**:
- PostgreSQL for multi-user
- Redis for session storage
- Celery for async processing
- Load balancer for scaling

## Security Considerations

1. **API Keys**: Environment variables only
2. **Input Validation**: All user inputs validated
3. **SQL Injection**: Parameterized queries
4. **File Upload**: Type and size restrictions
5. **Logging**: No sensitive data in logs

## Performance Optimizations

1. **Database Indexes**: Fast searches
2. **Connection Pooling**: Reuse connections
3. **Lazy Loading**: Initialize on demand
4. **Caching**: Session state for components
5. **Async Processing**: Progress indicators

## Monitoring and Observability

**Logging Levels**:
- DEBUG: Detailed diagnostic info
- INFO: General informational messages
- WARNING: Warning messages
- ERROR: Error messages
- CRITICAL: Critical failures

**Metrics to Monitor**:
- Invoice processing time
- API call latency
- Database query performance
- Error rates
- Success rates

