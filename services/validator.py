"""
Validation Service
Validates invoice data for arithmetic accuracy
"""
import logging
from typing import Tuple
from models.invoice import InvoiceData

logger = logging.getLogger(__name__)


class ValidationService:
    """Service for validating invoice calculations."""
    
    def __init__(self, tolerance: float = 0.5):
        """
        Initialize validator.
        
        Args:
            tolerance: Maximum allowed difference for validation (default 0.5)
        """
        self.tolerance = tolerance
    
    def validate(self, invoice: InvoiceData) -> Tuple[bool, str]:
        """
        Validate invoice calculations.
        
        Formula: Σ(item.unit_price × item.quantity) - discount + tax = total
        
        Returns:
            (is_valid, message)
        """
        try:
            # Calculate items total
            calculated_subtotal = sum(
                item.unit_price * item.quantity 
                for item in invoice.items
            )
            
            # Calculate expected total (subtotal - discount + tax)
            calculated_total = calculated_subtotal - invoice.discount + invoice.tax_amount
            
            # Check subtotal
            subtotal_diff = abs(calculated_subtotal - invoice.subtotal)
            
            # Check total
            total_diff = abs(calculated_total - invoice.total_amount)
            
            logger.info(
                f"Validation: calculated_subtotal={calculated_subtotal:.2f}, "
                f"invoice_subtotal={invoice.subtotal:.2f}, "
                f"discount={invoice.discount:.2f}, "
                f"diff={subtotal_diff:.2f}"
            )
            
            logger.info(
                f"Validation: calculated_total={calculated_total:.2f}, "
                f"invoice_total={invoice.total_amount:.2f}, "
                f"diff={total_diff:.2f}"
            )
            
            # Determine validation result
            if subtotal_diff <= self.tolerance and total_diff <= self.tolerance:
                invoice.is_valid = True
                invoice.validation_message = "✅ الحسابات صحيحة"
                return True, invoice.validation_message
            
            elif subtotal_diff > self.tolerance:
                invoice.is_valid = False
                invoice.validation_message = (
                    f"⚠️ تحذير: فرق في المجموع الفرعي\n"
                    f"المحسوب: {calculated_subtotal:.2f}\n"
                    f"في الفاتورة: {invoice.subtotal:.2f}\n"
                    f"الفرق: {subtotal_diff:.2f}"
                )
                return False, invoice.validation_message
            
            else:
                invoice.is_valid = False
                invoice.validation_message = (
                    f"⚠️ تحذير: فرق في الإجمالي النهائي\n"
                    f"المحسوب: {calculated_total:.2f}\n"
                    f"في الفاتورة: {invoice.total_amount:.2f}\n"
                    f"الفرق: {total_diff:.2f}"
                )
                return False, invoice.validation_message
                
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            invoice.is_valid = False
            invoice.validation_message = f"❌ خطأ في التدقيق: {str(e)}"
            return False, invoice.validation_message


# Global instance
validator = ValidationService()