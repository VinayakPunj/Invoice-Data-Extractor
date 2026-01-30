# API Documentation

## Module Reference

This document provides detailed API documentation for all modules in the Invoice Data Extractor.

## Configuration Module (`config.py`)

### Class: `Config`

Central configuration class managing all application settings.

#### Class Attributes

| Attribute | Type | Default | Description |
|-----------|------|---------|-------------|
| `BASE_DIR` | Path | Project root | Base directory path |
| `GOOGLE_API_KEY` | str | '' | Google Generative AI API key |
| `TESSERACT_CMD` | str | Platform-specific | Path to Tesseract executable |
| `DATABASE_PATH` | str | 'invoices.db' | SQLite database file path |
| `APP_TITLE` | str | 'InvoiceIQ' | Application title |
| `MAX_PAGES_PER_PDF` | int | 10 | Maximum PDF pages to process |
| `LLM_MODEL` | str | 'gemini-2.0-flash-exp' | AI model name. Options: gemini-2.0-flash-exp, gemini-1.5-pro, gemini-1.5-flash, models/gemma-2-9b-it, models/gemma-2-27b-it, models/gemma-2-2b-it |
| `LLM_TEMPERATURE` | float | 0 | AI temperature setting |
| `LLM_TOP_P` | float | 0.95 | AI top_p setting |
| `LLM_TOP_K` | int | 64 | AI top_k setting |
| `LLM_MAX_OUTPUT_TOKENS` | int | 8192 | Max AI output tokens |
| `LOG_LEVEL` | str | 'INFO' | Logging level |
| `LOG_FILE` | str | 'app.log' | Log file path |

#### Methods

**`validate() -> List[str]`**

Validates configuration settings.

**Returns**: List of error messages (empty if valid)

**Example**:
```python
from config import Config

errors = Config.validate()
if errors:
    for error in errors:
        print(f"Error: {error}")
```

**`get_generation_config() -> Dict`**

Returns LLM generation configuration.

**Returns**: Dictionary with temperature, top_p, top_k, max_output_tokens

---

## Database Module (`src/database.py`)

### Class: `DatabaseManager`

Handles all database operations for invoice storage and retrieval.

#### Constructor

```python
DatabaseManager(db_path: str = None)
```

**Parameters**:
- `db_path` (str, optional): Path to SQLite database. Uses Config.DATABASE_PATH if not provided.

#### Methods

**`insert_invoice(company_name: str, invoice_date: str, total_amount: float) -> int`**

Insert a new invoice record.

**Parameters**:
- `company_name` (str): Company name
- `invoice_date` (str): Date in YYYY-MM-DD format
- `total_amount` (float): Invoice total amount

**Returns**: int - ID of inserted record

**Raises**: DatabaseError if insertion fails

**Example**:
```python
from src.database import DatabaseManager

db = DatabaseManager()
invoice_id = db.insert_invoice(
    company_name="Acme Corp",
    invoice_date="2024-01-15",
    total_amount=1500.50
)
```

**`search_invoices(from_date: str = None, to_date: str = None, company_name: str = None) -> List[Tuple]`**

Search invoices with optional filters.

**Parameters**:
- `from_date` (str, optional): Start date (YYYY-MM-DD)
- `to_date` (str, optional): End date (YYYY-MM-DD)
- `company_name` (str, optional): Company name (partial match)

**Returns**: List of tuples (id, company_name, invoice_date, total_amount)

**Example**:
```python
# Search by date range
results = db.search_invoices(
    from_date="2024-01-01",
    to_date="2024-01-31"
)

# Search by company name
results = db.search_invoices(company_name="Acme")
```

**`get_all_invoices() -> List[Tuple]`**

Retrieve all invoices.

**Returns**: List of all invoice tuples

**`delete_invoice(invoice_id: int) -> bool`**

Delete an invoice by ID.

**Parameters**:
- `invoice_id` (int): ID of invoice to delete

**Returns**: bool - True if successful

**`get_statistics() -> Dict[str, Any]`**

Get database statistics.

**Returns**: Dictionary with keys:
- `total_invoices` (int): Total number of invoices
- `total_amount` (float): Sum of all invoice amounts
- `unique_companies` (int): Number of unique companies

---

## OCR Module (`src/ocr.py`)

### Class: `OCRProcessor`

Handles OCR processing for PDF documents.

#### Constructor

```python
OCRProcessor(max_pages: int = None)
```

**Parameters**:
- `max_pages` (int, optional): Maximum pages to process. Uses Config.MAX_PAGES_PER_PDF if not provided.

#### Methods

**`extract_text_from_pdf(pdf_path: str) -> str`**

Extract text from PDF using OCR.

**Parameters**:
- `pdf_path` (str): Path to PDF file

**Returns**: str - Extracted text

**Raises**:
- `FileNotFoundError`: If PDF doesn't exist
- `Exception`: If OCR processing fails

**Example**:
```python
from src.ocr import OCRProcessor

ocr = OCRProcessor()
text = ocr.extract_text_from_pdf("invoice.pdf")
```

**`extract_text_from_image(image_path: str) -> str`**

Extract text from image file.

**Parameters**:
- `image_path` (str): Path to image file

**Returns**: str - Extracted text

**`process_uploaded_file(file_bytes: bytes, filename: str) -> str`**

Process uploaded file bytes.

**Parameters**:
- `file_bytes` (bytes): Raw file bytes
- `filename` (str): Original filename

**Returns**: str - Extracted text

**Static Methods**

**`validate_tesseract_installation() -> bool`**

Check Tesseract installation.

**Returns**: bool - True if Tesseract is available

---

## LLM Module (`src/llm.py`)

### Class: `InvoiceExtractor`

Extracts structured data from invoice text using AI.

#### Constructor

```python
InvoiceExtractor()
```

Initializes with Google Generative AI configuration.

#### Methods

**`extract_invoice_data(invoice_text: str) -> Dict[str, str]`**

Extract structured invoice data from text.

**Parameters**:
- `invoice_text` (str): Raw text from invoice

**Returns**: Dictionary with keys:
- `company_name` (str): Extracted company name
- `invoice_date` (str): Extracted date
- `total_amount` (str): Extracted amount

**Example**:
```python
from src.llm import InvoiceExtractor

extractor = InvoiceExtractor()
data = extractor.extract_invoice_data(invoice_text)
print(f"Company: {data['company_name']}")
```

**Static Methods**

**`validate_api_key() -> bool`**

Validate API key configuration.

**Returns**: bool - True if API key is set

---

## Utilities Module (`src/utils.py`)

### Class: `DateParser`

Multi-format date parsing utility.

#### Class Methods

**`parse_date(date_str: str) -> Optional[str]`**

Parse date string to YYYY-MM-DD format.

**Parameters**:
- `date_str` (str): Date in various formats

**Returns**: str in YYYY-MM-DD format or None if parsing fails

**Supported Formats**:
- DD-Mon-YY (17-Jun-24)
- DD-MM-YYYY (17-06-2024)
- DD.MM.YYYY (17.06.2024)
- DD/MM/YYYY (17/06/2024)
- YYYY-MM-DD (2024-06-17)
- Month DD, YYYY (June 17, 2024)
- And more...

**Example**:
```python
from src.utils import DateParser

date = DateParser.parse_date("17-Jun-24")
# Returns: "2024-06-17"
```

**`format_date_for_display(date_str: str, format_str: str = '%d-%m-%Y') -> str`**

Format date for display.

**`validate_date_range(from_date: str, to_date: str) -> bool`**

Validate date range.

---

### Class: `AmountParser`

Currency amount parsing utility.

#### Static Methods

**`parse_amount(amount_str: str) -> Optional[float]`**

Parse amount string to float.

**Parameters**:
- `amount_str` (str): Amount with optional currency symbols

**Returns**: float or None if parsing fails

**Handles**:
- Currency symbols ($, €, etc.)
- Thousands separators (,)
- Decimal separators (. or ,)
- Various formats

**Example**:
```python
from src.utils import AmountParser

amount = AmountParser.parse_amount("$1,500.50")
# Returns: 1500.5
```

**`format_amount(amount: float, currency: str = '$') -> str`**

Format amount for display.

---

### Class: `Validator`

Data validation utilities.

#### Static Methods

**`validate_company_name(company_name: str) -> bool`**

Validate company name.

**`validate_invoice_data(data: dict) -> Tuple[bool, List[str]]`**

Validate complete invoice data.

**Parameters**:
- `data` (dict): Invoice data dictionary

**Returns**: Tuple of (is_valid, error_list)

**Example**:
```python
from src.utils import Validator

data = {
    'company_name': 'Acme Corp',
    'invoice_date': '17-Jun-24',
    'total_amount': '1500.50'
}

is_valid, errors = Validator.validate_invoice_data(data)
if not is_valid:
    print("Errors:", errors)
```

---

## Logger Module (`src/logger.py`)

### Function: `setup_logger`

```python
setup_logger(name: str = __name__) -> logging.Logger
```

Set up and configure logger.

**Parameters**:
- `name` (str): Logger name (default: module name)

**Returns**: Configured Logger instance

**Features**:
- Console output (INFO level)
- File output (DEBUG level)
- Formatted timestamps
- Context information

**Example**:
```python
from src.logger import setup_logger

logger = setup_logger(__name__)
logger.info("Processing started")
logger.error("An error occurred")
```

---

## Usage Examples

### Complete Invoice Processing

```python
from config import Config
from src.database import DatabaseManager
from src.ocr import OCRProcessor
from src.llm import InvoiceExtractor
from src.utils import DateParser, AmountParser

# Initialize components
db = DatabaseManager()
ocr = OCRProcessor()
llm = InvoiceExtractor()

# Process invoice
text = ocr.extract_text_from_pdf("invoice.pdf")
data = llm.extract_invoice_data(text)

# Validate and parse
date = DateParser.parse_date(data['invoice_date'])
amount = AmountParser.parse_amount(data['total_amount'])

# Save to database
if date and amount:
    invoice_id = db.insert_invoice(
        company_name=data['company_name'],
        invoice_date=date,
        total_amount=amount
    )
    print(f"Saved invoice {invoice_id}")
```

### Search and Export

```python
from src.database import DatabaseManager
import pandas as pd

db = DatabaseManager()

# Search invoices
results = db.search_invoices(
    from_date="2024-01-01",
    to_date="2024-12-31",
    company_name="Acme"
)

# Convert to DataFrame
df = pd.DataFrame(
    results,
    columns=["ID", "Company", "Date", "Amount"]
)

# Export
df.to_csv("invoices.csv", index=False)
```

---

## Error Handling

All modules raise appropriate exceptions:

- `FileNotFoundError`: File doesn't exist
- `ValueError`: Invalid input data
- `Exception`: General errors with descriptive messages

Always wrap calls in try-except blocks:

```python
try:
    result = function_call()
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```
