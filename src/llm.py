"""
LLM integration module for Invoice Data Extractor.
Handles AI-powered invoice data extraction using Google Generative AI.
"""
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from typing import Dict, Optional
import re

from config import Config
from src.logger import setup_logger

logger = setup_logger(__name__)

# Configure Generative AI
genai.configure(api_key=Config.GOOGLE_API_KEY)


class InvoiceExtractor:
    """Extracts structured data from invoice text using LLM."""
    
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
    
    def __init__(self):
        """Initialize the invoice extractor."""
        self.model = self._create_model()
        logger.info("Invoice Extractor initialized")
    
    def _create_model(self):
        """
        Create and configure the generative AI model.
        
        Returns:
            Configured GenerativeModel instance
        """
        # Compatible with both old and new versions of google-generativeai
        try:
            # Try new version with system_instruction
            model = genai.GenerativeModel(
                model_name=Config.LLM_MODEL,
                generation_config=Config.get_generation_config(),
                system_instruction=self.SYSTEM_INSTRUCTION,
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                }
            )
        except TypeError:
            # Fallback for older versions without system_instruction
            logger.info("Using older API version without system_instruction parameter")
            model = genai.GenerativeModel(
                model_name=Config.LLM_MODEL,
                generation_config=Config.get_generation_config(),
                safety_settings={
                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                }
            )
        return model
    
    def extract_invoice_data(self, invoice_text: str) -> Dict[str, str]:
        """
        Extract structured invoice data from text.
        
        Args:
            invoice_text: Raw text extracted from invoice
            
        Returns:
            Dictionary with company_name, invoice_date, and total_amount
        """
        try:
            logger.info("Sending invoice text to LLM for extraction")
            
            # Generate content using the model
            # Include system instruction in prompt for compatibility
            full_prompt = f"{self.SYSTEM_INSTRUCTION}\n\n{self.EXTRACTION_PROMPT}"
            prompt_parts = [invoice_text, full_prompt]
            response = self.model.generate_content(prompt_parts)
            
            if response is None or not response.text:
                logger.warning("No valid response from LLM")
                if response and hasattr(response, 'candidate') and hasattr(response.candidate, 'safety_ratings'):
                    safety_ratings = response.candidate.safety_ratings
                    logger.error(f'Generation blocked due to safety ratings: {safety_ratings}')
                return self._get_default_data()
            
            llm_output = response.text
            logger.debug(f"LLM Output: {llm_output}")
            
            # Parse the LLM output
            extracted_data = self._parse_llm_output(llm_output)
            logger.info(f"Successfully extracted data: {extracted_data}")
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            return self._get_default_data()
    
    def _parse_llm_output(self, llm_output: str) -> Dict[str, str]:
        """
        Parse LLM output to extract structured data.
        
        Args:
            llm_output: Raw output from LLM
            
        Returns:
            Dictionary with extracted fields
        """
        # Regex patterns to match the expected format
        company_name_match = re.search(r"Company name:\s*([^\n]+?)\s*Invoice date:", llm_output)
        date_match = re.search(r"Invoice date:\s*([^\n]+?)\s*Total amount:", llm_output)
        total_amount_match = re.search(r"Total amount:\s*([^\n]+?)(?:\n|$)", llm_output)
        
        company_name = company_name_match.group(1).strip() if company_name_match else "Unknown"
        invoice_date = date_match.group(1).strip() if date_match else "Unknown"
        total_amount = total_amount_match.group(1).strip() if total_amount_match else "Unknown"
        
        # Clean up total amount (remove currency symbols, commas)
        if total_amount != "Unknown":
            # Extract numeric value with optional decimal
            amount_numeric = re.search(r"([\d,]+\.?\d*)", total_amount)
            if amount_numeric:
                total_amount = amount_numeric.group(1).replace(",", "")
        
        return {
            'company_name': company_name,
            'invoice_date': invoice_date,
            'total_amount': total_amount
        }
    
    @staticmethod
    def _get_default_data() -> Dict[str, str]:
        """
        Get default data structure when extraction fails.
        
        Returns:
            Dictionary with 'Unknown' values
        """
        return {
            'company_name': 'Unknown',
            'invoice_date': 'Unknown',
            'total_amount': 'Unknown'
        }
    
    @staticmethod
    def validate_api_key() -> bool:
        """
        Validate that API key is configured.
        
        Returns:
            True if API key is set
        """
        is_valid = bool(Config.GOOGLE_API_KEY)
        if is_valid:
            logger.info("Google API key is configured")
        else:
            logger.error("Google API key is not configured")
        return is_valid
