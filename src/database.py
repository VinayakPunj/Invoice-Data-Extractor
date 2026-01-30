"""
Database operations module for Invoice Data Extractor.
Handles all SQLite database interactions.
"""
import sqlite3
from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
from contextlib import contextmanager
from datetime import datetime

from config import Config
from src.logger import setup_logger

logger = setup_logger(__name__)


class DatabaseManager:
    """Manages database operations for invoice storage and retrieval."""
    
    def __init__(self, db_path: str = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file. Uses config default if not provided.
        """
        self.db_path = db_path or Config.DATABASE_PATH
        self._initialize_database()
    
    @contextmanager
    def get_connection(self):
        """
        Context manager for database connections.
        Ensures proper connection cleanup.
        
        Yields:
            SQLite connection object
        """
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def _initialize_database(self):
        """Create database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS invoices (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT NOT NULL,
                    invoice_date DATE NOT NULL,
                    total_amount DECIMAL(10, 2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create index for faster searches
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_invoice_date 
                ON invoices(invoice_date)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_company_name 
                ON invoices(company_name)
            ''')
            
            logger.info("Database initialized successfully")
    
    def insert_invoice(
        self, 
        company_name: str, 
        invoice_date: str, 
        total_amount: float
    ) -> int:
        """
        Insert a new invoice record.
        
        Args:
            company_name: Name of the company
            invoice_date: Invoice date in YYYY-MM-DD format
            total_amount: Total amount on invoice
            
        Returns:
            ID of the inserted record
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO invoices (company_name, invoice_date, total_amount) VALUES (?, ?, ?)',
                (company_name, invoice_date, total_amount)
            )
            invoice_id = cursor.lastrowid
            logger.info(f"Inserted invoice {invoice_id} for {company_name}")
            return invoice_id
    
    def search_invoices(
        self,
        from_date: Optional[str] = None,
        to_date: Optional[str] = None,
        company_name: Optional[str] = None
    ) -> List[Tuple]:
        """
        Search invoices by date range and/or company name.
        
        Args:
            from_date: Start date (YYYY-MM-DD)
            to_date: End date (YYYY-MM-DD)
            company_name: Company name to search for (partial match)
            
        Returns:
            List of invoice tuples (id, company_name, invoice_date, total_amount)
        """
        query = "SELECT id, company_name, invoice_date, total_amount FROM invoices WHERE 1=1"
        params = []
        
        if from_date:
            query += " AND invoice_date >= ?"
            params.append(from_date)
        
        if to_date:
            query += " AND invoice_date <= ?"
            params.append(to_date)
        
        if company_name:
            query += " AND company_name LIKE ?"
            params.append(f"%{company_name}%")
        
        query += " ORDER BY invoice_date DESC"
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            logger.info(f"Search returned {len(results)} results")
            return results
    
    def get_all_invoices(self) -> List[Tuple]:
        """
        Get all invoices from the database.
        
        Returns:
            List of all invoice tuples
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, company_name, invoice_date, total_amount FROM invoices ORDER BY invoice_date DESC"
            )
            return cursor.fetchall()
    
    def delete_invoice(self, invoice_id: int) -> bool:
        """
        Delete an invoice by ID.
        
        Args:
            invoice_id: ID of invoice to delete
            
        Returns:
            True if deletion was successful
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM invoices WHERE id = ?", (invoice_id,))
            deleted = cursor.rowcount > 0
            if deleted:
                logger.info(f"Deleted invoice {invoice_id}")
            return deleted
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get database statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM invoices")
            total_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT SUM(total_amount) FROM invoices")
            total_amount = cursor.fetchone()[0] or 0
            
            cursor.execute("SELECT COUNT(DISTINCT company_name) FROM invoices")
            unique_companies = cursor.fetchone()[0]
            
            return {
                'total_invoices': total_count,
                'total_amount': total_amount,
                'unique_companies': unique_companies
            }
