"""Tests for utility functions."""
import pytest
from src.utils import DateParser, AmountParser, Validator


class TestDateParser:
    """Tests for DateParser class."""
    
    def test_parse_various_formats(self):
        """Test parsing various date formats."""
        test_cases = [
            ("17-Jun-24", "2024-06-17"),
            ("17-06-2024", "2024-06-17"),
            ("17.06.2024", "2024-06-17"),
            ("17/06/2024", "2024-06-17"),
            ("2024-06-17", "2024-06-17"),
            ("June 17, 2024", "2024-06-17"),
            ("17 Jun 2024", "2024-06-17"),
        ]
        
        for input_date, expected in test_cases:
            result = DateParser.parse_date(input_date)
            assert result == expected, f"Failed for {input_date}"
    
    def test_parse_invalid_date(self):
        """Test parsing invalid date returns None."""
        assert DateParser.parse_date("invalid") is None
        assert DateParser.parse_date("Unknown") is None
        assert DateParser.parse_date("") is None
    
    def test_validate_date_range(self):
        """Test date range validation."""
        assert DateParser.validate_date_range("2024-01-01", "2024-12-31") is True
        assert DateParser.validate_date_range("2024-06-15", "2024-06-15") is True
        assert DateParser.validate_date_range("2024-12-31", "2024-01-01") is False


class TestAmountParser:
    """Tests for AmountParser class."""
    
    def test_parse_various_amounts(self):
        """Test parsing various amount formats."""
        test_cases = [
            ("1500.50", 1500.50),
            ("1,500.50", 1500.50),
            ("$1,500.50", 1500.50),
            ("1500", 1500.0),
            ("€ 2,500.75", 2500.75),
            ("1.500,50", 1500.50),  # European format
        ]
        
        for input_amount, expected in test_cases:
            result = AmountParser.parse_amount(input_amount)
            assert result == pytest.approx(expected), f"Failed for {input_amount}"
    
    def test_parse_invalid_amount(self):
        """Test parsing invalid amount returns None."""
        assert AmountParser.parse_amount("invalid") is None
        assert AmountParser.parse_amount("Unknown") is None
        assert AmountParser.parse_amount("") is None
    
    def test_format_amount(self):
        """Test amount formatting."""
        assert AmountParser.format_amount(1500.50) == "$1,500.50"
        assert AmountParser.format_amount(1000) == "$1,000.00"


class TestValidator:
    """Tests for Validator class."""
    
    def test_validate_company_name(self):
        """Test company name validation."""
        assert Validator.validate_company_name("Valid Company") is True
        assert Validator.validate_company_name("ABC Corp") is True
        assert Validator.validate_company_name("") is False
        assert Validator.validate_company_name("Unknown") is False
        assert Validator.validate_company_name("   ") is False
    
    def test_validate_invoice_data(self):
        """Test complete invoice data validation."""
        valid_data = {
            'company_name': 'Test Company',
            'invoice_date': '17-Jun-24',
            'total_amount': '1500.50'
        }
        
        is_valid, errors = Validator.validate_invoice_data(valid_data)
        assert is_valid is True
        assert len(errors) == 0
        
        invalid_data = {
            'company_name': 'Unknown',
            'invoice_date': 'invalid',
            'total_amount': 'abc'
        }
        
        is_valid, errors = Validator.validate_invoice_data(invalid_data)
        assert is_valid is False
        assert len(errors) > 0
