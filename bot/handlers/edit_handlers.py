"""
Edit Handlers
Message handlers for editing invoice fields
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.states.invoice_states import InvoiceStates
from bot.keyboards.invoice_keyboard import get_invoice_confirmation_keyboard, get_edit_menu_keyboard
from bot.handlers.invoice import format_invoice_result
from utils.calculations import recalculate_invoice

logger = logging.getLogger(__name__)
router = Router()


async def update_invoice_display(message: Message, state: FSMContext):
    """Update invoice display with new data."""
    data = await state.get_data()
    invoice = data.get("invoice_data")
    message_id = data.get("message_id")
    
    if invoice and message_id:
        result_text = format_invoice_result(invoice)
        try:
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message_id,
                text=result_text,
                parse_mode="MarkdownV2",
                reply_markup=get_edit_menu_keyboard()
            )
        except Exception as e:
            logger.error(f"Failed to update message: {e}")


@router.message(InvoiceStates.editing_supplier)
async def process_supplier_edit(message: Message, state: FSMContext):
    """Process supplier name edit."""
    data = await state.get_data()
    invoice = data.get("invoice_data")
    
    if invoice:
        invoice.supplier_name = message.text
        await state.update_data(invoice_data=invoice)
        await message.answer("✅ تم تحديث اسم المورد")
        await update_invoice_display(message, state)
        await state.set_state(InvoiceStates.waiting_confirmation)


@router.message(InvoiceStates.editing_date)
async def process_date_edit(message: Message, state: FSMContext):
    """Process date edit."""
    data = await state.get_data()
    invoice = data.get("invoice_data")
    
    if invoice:
        invoice.invoice_date = message.text
        await state.update_data(invoice_data=invoice)
        await message.answer("✅ تم تحديث التاريخ")
        await update_invoice_display(message, state)
        await state.set_state(InvoiceStates.waiting_confirmation)


@router.message(InvoiceStates.editing_invoice_number)
async def process_invoice_num_edit(message: Message, state: FSMContext):
    """Process invoice number edit."""
    data = await state.get_data()
    invoice = data.get("invoice_data")
    
    if invoice:
        invoice.invoice_number = message.text
        await state.update_data(invoice_data=invoice)
        await message.answer("✅ تم تحديث رقم الفاتورة")
        await update_invoice_display(message, state)
        await state.set_state(InvoiceStates.waiting_confirmation)


@router.message(InvoiceStates.editing_tax_number)
async def process_tax_num_edit(message: Message, state: FSMContext):
    """Process tax number edit."""
    data = await state.get_data()
    invoice = data.get("invoice_data")
    
    if invoice:
        invoice.tax_number = message.text
        await state.update_data(invoice_data=invoice)
        await message.answer("✅ تم تحديث الرقم الضريبي")
        await update_invoice_display(message, state)
        await state.set_state(InvoiceStates.waiting_confirmation)


@router.message(InvoiceStates.editing_subtotal)
async def process_subtotal_edit(message: Message, state: FSMContext):
    """Process subtotal edit."""
    try:
        new_value = float(message.text)
        data = await state.get_data()
        invoice = data.get("invoice_data")
        
        if invoice:
            invoice.subtotal = new_value
            await state.update_data(invoice_data=invoice)
            await message.answer("✅ تم تحديث المجموع الفرعي")
            await update_invoice_display(message, state)
            await state.set_state(InvoiceStates.waiting_confirmation)
    except ValueError:
        await message.answer("❌ قيمة غير صحيحة. أدخل رقماً صحيحاً.")


@router.message(InvoiceStates.editing_discount)
async def process_discount_edit(message: Message, state: FSMContext):
    """Process discount edit."""
    try:
        new_value = float(message.text)
        data = await state.get_data()
        invoice = data.get("invoice_data")
        
        if invoice:
            invoice.discount = new_value
            
            # Recalculate total
            recalculate_invoice(invoice)
            
            await state.update_data(invoice_data=invoice)
            await message.answer("✅ تم تحديث الخصم")
            await update_invoice_display(message, state)
            await state.set_state(InvoiceStates.waiting_confirmation)
    except ValueError:
        await message.answer("❌ قيمة غير صحيحة. أدخل رقماً صحيحاً.")


@router.message(InvoiceStates.editing_tax)
async def process_tax_edit(message: Message, state: FSMContext):
    """Process tax edit."""
    try:
        new_value = float(message.text)
        data = await state.get_data()
        invoice = data.get("invoice_data")
        
        if invoice:
            invoice.tax_amount = new_value
            
            # Recalculate total
            recalculate_invoice(invoice)
            
            await state.update_data(invoice_data=invoice)
            await message.answer("✅ تم تحديث الضريبة")
            await update_invoice_display(message, state)
            await state.set_state(InvoiceStates.waiting_confirmation)
    except ValueError:
        await message.answer("❌ قيمة غير صحيحة. أدخل رقماً صحيحاً.")


@router.message(InvoiceStates.editing_total)
async def process_total_edit(message: Message, state: FSMContext):
    """Process total edit."""
    try:
        new_value = float(message.text)
        data = await state.get_data()
        invoice = data.get("invoice_data")
        
        if invoice:
            invoice.total_amount = new_value
            await state.update_data(invoice_data=invoice)
            await message.answer("✅ تم تحديث الإجمالي النهائي")
            await update_invoice_display(message, state)
            await state.set_state(InvoiceStates.waiting_confirmation)
    except ValueError:
        await message.answer("❌ قيمة غير صحيحة. أدخل رقماً صحيحاً.")
