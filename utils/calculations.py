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
    - invoice.tax_amount = (subtotal - discount) * tax_rate / 100
    - invoice.total_amount = subtotal - discount + tax_amount
    """
    # Recalculate each item total
    for item in invoice.items:
        item.total = round(item.quantity * item.unit_price, 2)
    
    # Recalculate subtotal
    invoice.subtotal = round(sum(item.total for item in invoice.items), 2)
    
    # Recalculate tax amount based on tax_rate
    taxable_amount = invoice.subtotal - invoice.discount
    invoice.tax_amount = round(taxable_amount * invoice.tax_rate / 100, 2)
    
    # Recalculate total amount
    invoice.total_amount = round(
        invoice.subtotal - invoice.discount + invoice.tax_amount,
        2
    )
    
    return invoice
