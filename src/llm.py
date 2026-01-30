"""
LLM integration module for Invoice Data Extractor.
Handles AI-powered invoice data extraction using multiple providers:
Google Generative AI (Gemini), Ollama (Local), and OpenAI.
"""
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from openai import OpenAI
import requests
from typing import Dict, Optional, Any
import re
import json

from config import Config
from src.ollama_client import OllamaClient
from src.logger import setup_logger

logger = setup_logger(__name__)

class InvoiceExtractor:
    """Extracts structured data from invoice text using various LLM providers."""
    
    SYSTEM_INSTRUCTION = """
    You are an invoice examiner. Your job is to interpret the text of an invoice and extract 
    the information from the document accurately and precisely.
    """
    
    EXTRACTION_PROMPT = """Extract the company name, invoice date, and total amount from the invoice. 
    Only return the required information without adding extra words or sentences.
    The output should strictly follow this format:
    Company name: <company_name> Invoice date: <invoice_date> Total amount: <total_amount>

    Ensure:
    - The company name is enclosed within `Company name:`
    - The invoice date is enclosed within `Invoice date:`
    - The total amount is enclosed within `Total amount:`
    - No extra text or comments are included.
    - Use the exact field names and order as provided above.
    """
    
    def __init__(self, provider: str = None, model_name: str = None, api_key: str = None):
        """
        Initialize the invoice extractor.
        
        Args:
            provider: LLM provider ('google', 'ollama', 'openai')
            model_name: Name of the model to use
            api_key: API key for the provider (if required)
        """
        self.provider = provider or Config.DEFAULT_PROVIDER
        self.model_name = model_name or Config.LLM_MODEL
        self.api_key = api_key
        
        self.logger = logger
        self.logger.info(f"Initializing Invoice Extractor with provider: {self.provider}, model: {self.model_name}")
        
        # Initialize provider-specific clients
        self._setup_provider()

    def _setup_provider(self):
        """Configure the selected provider and initialize its client."""
        try:
            if self.provider == 'google':
                key = self.api_key or Config.GOOGLE_API_KEY
                if key:
                    genai.configure(api_key=key)
                    self.client = self._create_google_model()
                else:
                    self.client = None
                    self.logger.warning("Google API key not provided")
            
            elif self.provider == 'ollama':
                self.client = OllamaClient(base_url=Config.OLLAMA_BASE_URL)
                
            elif self.provider == 'openai':
                key = self.api_key or Config.OPENAI_API_KEY
                if key:
                    self.client = OpenAI(api_key=key)
                else:
                    self.client = None
                    self.logger.warning("OpenAI API key not provided")
            
            else:
                self.logger.error(f"Unsupported provider: {self.provider}")
                self.client = None
        except Exception as e:
            self.logger.error(f"Failed to setup provider {self.provider}: {e}")
            self.client = None

    def _create_google_model(self):
        """Create and configure the Google GenerativeModel."""
        try:
            return genai.GenerativeModel(
                model_name=self.model_name,
                generation_config=Config.get_generation_config(),
                system_instruction=self.SYSTEM_INSTRUCTION,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                }
            )
        except Exception as e:
            self.logger.error(f"Error creating Gemini model: {e}")
            # Fallback for older versions or other issues
            return genai.GenerativeModel(model_name=self.model_name)

    def extract_invoice_data(self, invoice_text: str) -> Dict[str, str]:
        """
        Extract structured invoice data from text using the selected provider.
        
        Args:
            invoice_text: Raw text extracted from invoice
            
        Returns:
            Dictionary with company_name, invoice_date, and total_amount
        """
        if not self.client:
            self.logger.error(f"Client not initialized for provider: {self.provider}")
            return self._get_default_data()

        try:
            self.logger.info(f"Extracting data using {self.provider} ({self.model_name})")
            
            if self.provider == 'google':
                return self._generate_with_google(invoice_text)
            elif self.provider == 'ollama':
                return self._generate_with_ollama(invoice_text)
            elif self.provider == 'openai':
                return self._generate_with_openai(invoice_text)
            
            return self._get_default_data()
            
        except Exception as e:
            self.logger.error(f"Extraction failed: {e}")
            return self._get_default_data()

    def _generate_with_google(self, invoice_text: str) -> Dict[str, str]:
        """Generate content using Google Gemini."""
        full_prompt = f"{self.SYSTEM_INSTRUCTION}\n\n{self.EXTRACTION_PROMPT}\n\nInvoice Text:\n{invoice_text}"
        response = self.client.generate_content(full_prompt)
        
        if response and response.text:
            return self._parse_llm_output(response.text)
        return self._get_default_data()

    def _generate_with_ollama(self, invoice_text: str) -> Dict[str, str]:
        """Generate content using local Ollama model."""
        options = {
            "temperature": Config.LLM_TEMPERATURE,
            "top_p": Config.LLM_TOP_P,
            "top_k": Config.LLM_TOP_K,
            "num_predict": Config.LLM_MAX_OUTPUT_TOKENS
        }
        
        response = self.client.generate(
            model=self.model_name,
            prompt=f"{self.EXTRACTION_PROMPT}\n\nInvoice Text:\n{invoice_text}",
            system=self.SYSTEM_INSTRUCTION,
            options=options
        )
        
        if response:
            return self._parse_llm_output(response)
        return self._get_default_data()

    def _generate_with_openai(self, invoice_text: str) -> Dict[str, str]:
        """Generate content using OpenAI GPT models."""
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": self.SYSTEM_INSTRUCTION},
                {"role": "user", "content": f"{self.EXTRACTION_PROMPT}\n\nInvoice Text:\n{invoice_text}"}
            ],
            temperature=Config.LLM_TEMPERATURE,
            max_tokens=Config.LLM_MAX_OUTPUT_TOKENS
        )
        
        if response and response.choices:
            return self._parse_llm_output(response.choices[0].message.content)
        return self._get_default_data()

    def _parse_llm_output(self, llm_output: str) -> Dict[str, str]:
        """Parse LLM output to extract structured data."""
        self.logger.debug(f"Parsing LLM output: {llm_output}")
        
        # Regex patterns to match the expected format
        patterns = {
            'company_name': r"Company name:\s*([^\n]+?)\s*Invoice date:",
            'invoice_date': r"Invoice date:\s*([^\n]+?)\s*Total amount:",
            'total_amount': r"Total amount:\s*([^\n]+?)(?:\n|$)"
        }
        
        results = {}
        for field, pattern in patterns.items():
            match = re.search(pattern, llm_output, re.IGNORECASE)
            results[field] = match.group(1).strip() if match else "Unknown"
        
        # Clean up total amount
        if results['total_amount'] != "Unknown":
            amount_numeric = re.search(r"([\d,]+\.?\d*)", results['total_amount'])
            if amount_numeric:
                results['total_amount'] = amount_numeric.group(1).replace(",", "")
        
        return results

    @staticmethod
    def _get_default_data() -> Dict[str, str]:
        """Get default data structure when extraction fails."""
        return {
            'company_name': 'Unknown',
            'invoice_date': 'Unknown',
            'total_amount': 'Unknown'
        }

    @staticmethod
    def validate_api_key(provider: str, api_key: str = None) -> bool:
        """Validate that API key is configured for the provider."""
        if provider == 'google':
            return bool(api_key or Config.GOOGLE_API_KEY)
        elif provider == 'openai':
            return bool(api_key or Config.OPENAI_API_KEY)
        elif provider == 'ollama':
            return True # Ollama doesn't require API key
        return False

    def list_available_models(self) -> list[str]:
        """
        List available models for the current provider.
        
        Returns:
            List of model names
        """
        if self.provider == 'google':
            return self._list_google_models()
        elif self.provider == 'ollama':
            return self.client.list_models() if self.client else []
        elif self.provider == 'openai':
            return self._list_openai_models()
        return []

    def _list_google_models(self) -> list[str]:
        """List available Google Gemini models supporting generation."""
        try:
            key = self.api_key or Config.GOOGLE_API_KEY
            if not key:
                return []
            
            genai.configure(api_key=key)
            models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    # Filter out older models or non-text models if needed
                    if 'gemini' in m.name.lower():
                        models.append(m.name.replace('models/', ''))
            return sorted(models)
        except Exception as e:
            self.logger.error(f"Error listing Google models: {e}")
            return Config.AVAILABLE_MODELS.get('google', [])

    def _list_openai_models(self) -> list[str]:
        """List available OpenAI chat models."""
        try:
            key = self.api_key or Config.OPENAI_API_KEY
            if not key:
                return []
            
            if not self.client:
                self.client = OpenAI(api_key=key)
                
            models = self.client.models.list()
            # Filter for chat-compatible models
            chat_models = [
                m.id for m in models.data 
                if any(x in m.id.lower() for x in ['gpt-4', 'gpt-3.5'])
            ]
            return sorted(chat_models)
        except Exception as e:
            self.logger.error(f"Error listing OpenAI models: {e}")
            return Config.AVAILABLE_MODELS.get('openai', [])
