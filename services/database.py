"""
Database Service
SQLite database for storing invoices and items per user
"""
import sqlite3
import logging
from datetime import datetime
from typing import List, Optional, Tuple
from pathlib import Path
from models.invoice import InvoiceData, InvoiceItem

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for managing invoice database."""
    
    def __init__(self, db_path: str = "data/invoices.db"):
        """Initialize database service."""
        self.db_path = db_path
        # Create data directory if not exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.initialize_db()
    
    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        conn = sqlite3.Connection(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def initialize_db(self):
        """Create tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Invoices table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                supplier_name TEXT,
                tax_number TEXT,
                invoice_number TEXT,
                invoice_date TEXT,
                subtotal REAL DEFAULT 0,
                discount REAL DEFAULT 0,
                tax_amount REAL DEFAULT 0,
                total_amount REAL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Invoice items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                item_name TEXT,
                quantity REAL DEFAULT 0,
                unit TEXT,
                unit_price REAL DEFAULT 0,
                total REAL DEFAULT 0,
                invoice_date TEXT,
                FOREIGN KEY (invoice_id) REFERENCES invoices (id)
            )
        """)
        
        # Create indexes for better performance
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_invoices_user_id 
            ON invoices(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_invoices_date 
            ON invoices(invoice_date)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_user_id 
            ON invoice_items(user_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_items_date 
            ON invoice_items(invoice_date)
        """)
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
    
    def save_invoice(self, user_id: int, invoice: InvoiceData) -> int:
        """
        Save invoice to database.
        
        Args:
            user_id: Telegram user ID
            invoice: Invoice data
            
        Returns:
            invoice_id: ID of saved invoice
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Insert invoice
            cursor.execute("""
                INSERT INTO invoices (
                    user_id, supplier_name, tax_number, invoice_number,
                    invoice_date, subtotal, discount, tax_amount, total_amount
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                user_id,
                invoice.supplier_name,
                invoice.tax_number,
                invoice.invoice_number,
                invoice.invoice_date,
                invoice.subtotal,
                invoice.discount,
                invoice.tax_amount,
                invoice.total_amount
            ))
            
            invoice_id = cursor.lastrowid
            
            # Insert items
            for item in invoice.items:
                cursor.execute("""
                    INSERT INTO invoice_items (
                        invoice_id, user_id, item_name, quantity,
                        unit, unit_price, total, invoice_date
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    invoice_id,
                    user_id,
                    item.name,
                    item.quantity,
                    item.unit,
                    item.unit_price,
                    item.total,
                    invoice.invoice_date
                ))
            
            conn.commit()
            logger.info(f"Saved invoice {invoice_id} for user {user_id}")
            return invoice_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to save invoice: {e}")
            raise
        finally:
            conn.close()
    
    def get_user_invoices(
        self, 
        user_id: int, 
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Tuple]:
        """
        Get user's invoices, optionally filtered by date range.
        
        Args:
            user_id: Telegram user ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of invoice tuples
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM invoices WHERE user_id = ?"
        params = [user_id]
        
        if start_date:
            query += " AND invoice_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND invoice_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY invoice_date DESC, created_at DESC"
        
        cursor.execute(query, params)
        invoices = cursor.fetchall()
        conn.close()
        
        return invoices
    
    def get_user_items(
        self,
        user_id: int,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Tuple]:
        """
        Get user's items, optionally filtered by date range.
        
        Args:
            user_id: Telegram user ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of item tuples
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM invoice_items WHERE user_id = ?"
        params = [user_id]
        
        if start_date:
            query += " AND invoice_date >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND invoice_date <= ?"
            params.append(end_date)
        
        query += " ORDER BY invoice_date DESC"
        
        cursor.execute(query, params)
        items = cursor.fetchall()
        conn.close()
        
        return items
    
    def get_invoice_count(self, user_id: int) -> int:
        """Get total number of invoices for user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM invoices WHERE user_id = ?", (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count
    
    def check_duplicate_invoice(self, user_id: int, invoice_number: str, tax_number: str) -> bool:
        """
        Check if invoice already exists based on invoice_number + tax_number.
        
        Args:
            user_id: Telegram user ID
            invoice_number: Invoice number
            tax_number: Tax number (VAT number)
            
        Returns:
            True if duplicate exists, False otherwise
        """
        if not invoice_number or not tax_number:
            return False
        
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM invoices 
            WHERE user_id = ? AND invoice_number = ? AND tax_number = ?
        """, (user_id, invoice_number, tax_number))
        count = cursor.fetchone()[0]
        conn.close()
        return count > 0


# Global instance
db_service = DatabaseService()
