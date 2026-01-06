"""
Invoice Data Models
Defines the structure of extracted invoice data
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class InvoiceItem:
    """Represents a single item in the invoice."""
    name: str = ""
    quantity: float = 0.0
    unit: str = ""
    unit_price: float = 0.0
    total: float = 0.0


@dataclass
class InvoiceData:
    """Represents the complete invoice data."""
    # Supplier Information
    supplier_name: str = ""
    tax_number: str = ""
    
    # Invoice Details
    invoice_number: str = ""
    invoice_date: str = ""
    
    # Items
    items: List[InvoiceItem] = field(default_factory=list)
    
    # Totals
    subtotal: float = 0.0
    discount: float = 0.0
    tax_amount: float = 0.0
    total_amount: float = 0.0
    
    # Validation
    is_valid: bool = False
    validation_message: str = ""