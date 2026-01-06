"""
FSM States
Finite State Machine states for invoice editing
"""
from aiogram.fsm.state import State, StatesGroup


class InvoiceStates(StatesGroup):
    """States for invoice editing workflow."""
    # Waiting for user to confirm/edit/cancel
    waiting_confirmation = State()
    
    # Edit states
    editing_supplier = State()
    editing_date = State()
    editing_invoice_number = State()
    editing_tax_number = State()
    editing_subtotal = State()
    editing_discount = State()
    editing_tax = State()
    editing_total = State()
    
    # Item edit states
    editing_item_name = State()
    editing_item_quantity = State()
    editing_item_unit = State()
    editing_item_price = State()
    editing_item_total = State()
