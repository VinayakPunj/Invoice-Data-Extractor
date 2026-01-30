"""
Utility functions for Invoice Data Extractor.
Handles date parsing, validation, and data formatting.
"""
from datetime import datetime
from typing import Optional, Union
import re

from src.logger import setup_logger

logger = setup_logger(__name__)


class DateParser:
    """Handles various date format parsing and conversion."""
    
    # Supported date formats
    FORMATS = [
        '%d-%b-%y',      # 17-Jun-24
        '%d-%b-%Y',      # 17-Jun-2024
        '%d-%m-%Y',      # 17-06-2024
        '%d.%m.%Y',      # 17.06.2024
        '%d/%m/%Y',      # 17/06/2024
        '%Y-%m-%d',      # 2024-06-17
        '%m/%d/%Y',      # 06/17/2024
        '%B %d, %Y',     # June 17, 2024
        '%b %d, %Y',     # Jun 17, 2024
        '%d %B %Y',      # 17 June 2024
        '%d %b %Y',      # 17 Jun 2024
    ]
    
    @classmethod
    def parse_date(cls, date_str: str) -> Optional[str]:
        """
        Parse date string to YYYY-MM-DD format.
        
        Args:
            date_str: Date string in various formats
            
        Returns:
            Date in YYYY-MM-DD format or None if parsing fails
        """
        if not date_str or date_str == "Unknown":
            return None
        
        # Clean the date string
        date_str = date_str.strip()
        
        # Try all supported formats
        for fmt in cls.FORMATS:
            try:
                parsed_date = datetime.strptime(date_str, fmt)
                result = parsed_date.strftime('%Y-%m-%d')
                logger.debug(f"Parsed date '{date_str}' as '{result}' using format '{fmt}'")
                return result
            except ValueError:
                continue
        
        logger.warning(f"Failed to parse date: {date_str}")
        return None
    
    @classmethod
    def format_date_for_display(cls, date_str: str, format_str: str = '%d-%m-%Y') -> str:
        """
        Format date for display.
        
        Args:
            date_str: Date in YYYY-MM-DD format
            format_str: Desired output format
            
        Returns:
            Formatted date string
        """
        try:
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            return date_obj.strftime(format_str)
        except ValueError:
            return date_str
    
    @classmethod
    def validate_date_range(cls, from_date: str, to_date: str) -> bool:
        """
        Validate that from_date is before or equal to to_date.
        
        Args:
            from_date: Start date in YYYY-MM-DD format
            to_date: End date in YYYY-MM-DD format
            
        Returns:
            True if date range is valid
        """
        try:
            from_dt = datetime.strptime(from_date, '%Y-%m-%d')
            to_dt = datetime.strptime(to_date, '%Y-%m-%d')
            return from_dt <= to_dt
        except ValueError:
            return False


class AmountParser:
    """Handles amount parsing and validation."""
    
    @staticmethod
    def parse_amount(amount_str: str) -> Optional[float]:
        """
        Parse amount string to float.
        
        Args:
            amount_str: Amount string with potential currency symbols and formatting
            
        Returns:
            Parsed float value or None if parsing fails
        """
        if not amount_str or amount_str == "Unknown":
            return None
        
        try:
            # Remove currency symbols and whitespace
            cleaned = re.sub(r'[^\d.,\-]', '', amount_str)
            
            # Handle different decimal separators
            # If there are multiple dots/commas, assume the last one is decimal
            if cleaned.count('.') > 1:
                cleaned = cleaned.replace('.', '', cleaned.count('.') - 1)
            if cleaned.count(',') > 1:
                cleaned = cleaned.replace(',', '', cleaned.count(',') - 1)
            
            # Replace comma with dot for decimal
            if ',' in cleaned and '.' not in cleaned:
                cleaned = cleaned.replace(',', '.')
            elif ',' in cleaned and '.' in cleaned:
                # Determine which is decimal separator (last one wins)
                if cleaned.rindex(',') > cleaned.rindex('.'):
                    cleaned = cleaned.replace('.', '').replace(',', '.')
                else:
                    cleaned = cleaned.replace(',', '')
            
            amount = float(cleaned)
            logger.debug(f"Parsed amount '{amount_str}' as {amount}")
            return amount
            
        except (ValueError, AttributeError) as e:
            logger.warning(f"Failed to parse amount '{amount_str}': {e}")
            return None
    
    @staticmethod
    def format_amount(amount: float, currency: str = '$') -> str:
        """
        Format amount for display.
        
        Args:
            amount: Numeric amount
            currency: Currency symbol
            
        Returns:
            Formatted amount string
        """
        return f"{currency}{amount:,.2f}"


class Validator:
    """Data validation utilities."""
    
    @staticmethod
    def validate_company_name(company_name: str) -> bool:
        """
        Validate company name.
        
        Args:
            company_name: Company name string
            
        Returns:
            True if valid
        """
        return bool(company_name and company_name.strip() and company_name != "Unknown")
    
    @staticmethod
    def validate_invoice_data(data: dict) -> tuple[bool, list]:
        """
        Validate complete invoice data.
        
        Args:
            data: Dictionary with invoice data
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        if not Validator.validate_company_name(data.get('company_name', '')):
            errors.append("Invalid company name")
        
        if not DateParser.parse_date(data.get('invoice_date', '')):
            errors.append("Invalid invoice date")
        
        if not AmountParser.parse_amount(str(data.get('total_amount', ''))):
            errors.append("Invalid total amount")
        
        return (len(errors) == 0, errors)


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename by removing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove invalid filename characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    return sanitized
