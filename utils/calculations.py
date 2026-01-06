"""
Auto-Calculation Utility
Automatically calculates invoice totals
"""
from models.invoice import InvoiceData


def recalculate_invoice(invoice: InvoiceData) -> InvoiceData:
    """
    Recalculate all auto-calculated fields in invoice.
    
    Auto-calculated fields:
    - item.total = item.quantity * item.unit_price
    - invoice.subtotal = sum of all item totals
    - invoice.total_amount = subtotal - discount + tax
    """
    # Recalculate each item total
    for item in invoice.items:
        item.total = round(item.quantity * item.unit_price, 2)
    
    # Recalculate subtotal
    invoice.subtotal = round(sum(item.total for item in invoice.items), 2)
    
    # Recalculate total amount
    invoice.total_amount = round(
        invoice.subtotal - invoice.discount + invoice.tax_amount,
        2
    )
    
    return invoice
