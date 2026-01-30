# Setup Instructions for Invoice Data Extractor

## Quick Setup Guide

Follow these steps to set up and run the application:

### 1. Activate Virtual Environment

```powershell
# On Windows PowerShell
.\venv\Scripts\Activate.ps1

# If you get execution policy error, run this first:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```powershell
# Copy the example file
copy .env.example .env

# Edit .env file and add your Google API key:
# GOOGLE_API_KEY=your_actual_api_key_here
```

### 4. Run the Application

```powershell
streamlit run app.py
```

The application will open in your browser at `http://localhost:8501`

## Troubleshooting

### Python Not Found
If `py` or `python` commands don't work:
- Install Python from https://www.python.org/downloads/
- Make sure to check "Add Python to PATH" during installation

### PowerShell Execution Policy Error
If you can't activate venv due to execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Tesseract Not Found
Download and install Tesseract OCR:
- Windows: https://github.com/UB-Mannheim/tesseract/wiki
- Update `TESSERACT_CMD` in `.env` file with installation path
