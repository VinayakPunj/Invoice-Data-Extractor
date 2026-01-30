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
    # Available providers: google, ollama, openai
    DEFAULT_PROVIDER = os.getenv('DEFAULT_PROVIDER', 'google')
    
    # Provider-specific models
    AVAILABLE_MODELS = {
        'google': [],
        'ollama': [], # Will be populated dynamically by OllamaClient
        'openai': []
    }
    
    # API Keys (can be provided via .env or overridden in UI)
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    
    # Ollama Configuration
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    
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
        
        if not cls.GOOGLE_API_KEY and not cls.OPENAI_API_KEY:
            # We don't strictly require API keys if Ollama is used or if they'll be provided in UI
            pass
        
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
