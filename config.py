"""
Configuration management for Invoice Data Extractor.
Loads settings from environment variables with sensible defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class."""
    
    # Base directory
    BASE_DIR = Path(__file__).parent
    
    # Google Generative AI
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    
    # Tesseract OCR
    TESSERACT_CMD = os.getenv(
        'TESSERACT_CMD', 
        r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    )
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'invoices.db')
    
    # Application Settings
    APP_TITLE = os.getenv('APP_TITLE', 'InvoiceIQ')
    MAX_PAGES_PER_PDF = int(os.getenv('MAX_PAGES_PER_PDF', '10'))
    
    # LLM Model Configuration
    # Available models:
    # Gemini Models (Google AI):
    #   - gemini-2.0-flash-exp (latest experimental)
    #   - gemini-1.5-pro
    #   - gemini-1.5-flash
    # Gemma Models (Open-source, via Vertex AI or local deployment):
    #   - gemma-2-9b-it (instruction-tuned, 9B parameters)
    #   - gemma-2-27b-it (instruction-tuned, 27B parameters)
    #   - gemma-2-2b-it (instruction-tuned, 2B parameters - lightweight)
    #   - models/gemma-2-9b-it (via Google AI API)
    # Note: For Gemma models via Google AI API, use format: models/gemma-2-9b-it
    LLM_MODEL = os.getenv('LLM_MODEL', 'gemini-2.0-flash-exp')
    LLM_TEMPERATURE = float(os.getenv('LLM_TEMPERATURE', '0'))
    LLM_TOP_P = float(os.getenv('LLM_TOP_P', '0.95'))
    LLM_TOP_K = int(os.getenv('LLM_TOP_K', '64'))
    LLM_MAX_OUTPUT_TOKENS = int(os.getenv('LLM_MAX_OUTPUT_TOKENS', '8192'))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'app.log')
    
    @classmethod
    def validate(cls):
        """Validate critical configuration settings."""
        errors = []
        
        if not cls.GOOGLE_API_KEY:
            errors.append("GOOGLE_API_KEY is not set. Please set it in .env file.")
        
        if not Path(cls.TESSERACT_CMD).exists():
            errors.append(
                f"Tesseract executable not found at {cls.TESSERACT_CMD}. "
                "Please install Tesseract OCR or update the path in .env file."
            )
        
        return errors
    
    @classmethod
    def get_generation_config(cls):
        """Get LLM generation configuration."""
        return {
            "temperature": cls.LLM_TEMPERATURE,
            "top_p": cls.LLM_TOP_P,
            "top_k": cls.LLM_TOP_K,
            "max_output_tokens": cls.LLM_MAX_OUTPUT_TOKENS
        }
