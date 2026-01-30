"""Tests for database operations."""
import pytest
import tempfile
import os
from pathlib import Path

from src.database import DatabaseManager


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    db = DatabaseManager(db_path=path)
    yield db
    
    # Cleanup
    Path(path).unlink(missing_ok=True)


def test_database_initialization(temp_db):
    """Test database initialization creates tables."""
    with temp_db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='invoices'")
        assert cursor.fetchone() is not None


def test_insert_invoice(temp_db):
    """Test inserting an invoice."""
    invoice_id = temp_db.insert_invoice(
        company_name="Test Company",
        invoice_date="2024-01-15",
        total_amount=1500.50
    )
    
    assert invoice_id > 0


def test_search_invoices(temp_db):
    """Test searching invoices."""
    # Insert test data
    temp_db.insert_invoice("Company A", "2024-01-10", 1000.00)
    temp_db.insert_invoice("Company B", "2024-01-15", 2000.00)
    temp_db.insert_invoice("Company A", "2024-01-20", 1500.00)
    
    # Search by date range
    results = temp_db.search_invoices(from_date="2024-01-12", to_date="2024-01-18")
    assert len(results) == 1
    
    # Search by company name
    results = temp_db.search_invoices(company_name="Company A")
    assert len(results) == 2


def test_get_statistics(temp_db):
    """Test getting database statistics."""
    temp_db.insert_invoice("Company A", "2024-01-10", 1000.00)
    temp_db.insert_invoice("Company B", "2024-01-15", 2000.00)
    temp_db.insert_invoice("Company A", "2024-01-20", 1500.00)
    
    stats = temp_db.get_statistics()
    
    assert stats['total_invoices'] == 3
    assert stats['total_amount'] == 4500.00
    assert stats['unique_companies'] == 2


def test_delete_invoice(temp_db):
    """Test deleting an invoice."""
    invoice_id = temp_db.insert_invoice("Test Company", "2024-01-15", 1000.00)
    
    # Delete the invoice
    result = temp_db.delete_invoice(invoice_id)
    assert result is True
    
    # Verify it's deleted
    all_invoices = temp_db.get_all_invoices()
    assert len(all_invoices) == 0
