"""
Edit Handlers
Message handlers for editing invoice fields - in-place updates
"""
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from bot.states.invoice_states import InvoiceStates
from bot.keyboards.invoice_keyboard import get_edit_menu_keyboard
from bot.handlers.invoice import format_invoice_result
from utils.calculations import recalculate_invoice

logger = logging.getLogger(__name__)
router = Router()


async def update_invoice_in_place(message: Message, state: FSMContext, success_text: str = "✅ تم التحديث"):
    """Update the original invoice message in-place and delete prompt."""
    data = await state.get_data()
    invoice = data.get("invoice_data")
    message_id = data.get("message_id")
    prompt_message_id = data.get("prompt_message_id")
    confirmation_messages = data.get("confirmation_messages", [])
    
    if invoice and message_id:
        result_text = format_invoice_result(invoice)
        try:
            # Edit the original message in-place
            await message.bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message_id,
                text=result_text,
                parse_mode="MarkdownV2",
                reply_markup=get_edit_menu_keyboard()
            )
            
            # Delete user's input message
            try:
                await message.delete()
            except Exception:
                pass
            
            # Delete prompt message (like "📝 ادخل الكمية الجديدة:")
            if prompt_message_id:
                try:
                    await message.bot.delete_message(
                        chat_id=message.chat.id,
                        message_id=prompt_message_id
                    )
                except Exception:
                    pass
            
            # Send confirmation and track it for deletion on save
            confirm_msg = await message.answer(success_text)
            confirmation_messages.append(confirm_msg.message_id)
            await state.update_data(
                prompt_message_id=None,
                confirmation_messages=confirmation_messages
            )
            
        except Exception as e:
            logger.error(f"Failed to update message: {e}")
            await message.answer("❌ حدث خطأ أثناء التحديث")


@router.message(InvoiceStates.editing_supplier)
async def process_supplier_edit(message: Message, state: FSMContext):
    """Process supplier name edit."""
    data = await state.get_data()
    invoice = data.get("invoice_data")
    
    if invoice:
        invoice.supplier_name = message.text
        await state.update_data(invoice_data=invoice)
        await update_invoice_in_place(message, state, "✅ تم تحديث اسم المورد")
        await state.set_state(InvoiceStates.waiting_confirmation)


@router.message(InvoiceStates.editing_date)
async def process_date_edit(message: Message, state: FSMContext):
    """Process date edit."""
    data = await state.get_data()
    invoice = data.get("invoice_data")
    
    if invoice:
        invoice.invoice_date = message.text
        await state.update_data(invoice_data=invoice)
        await update_invoice_in_place(message, state, "✅ تم تحديث التاريخ")
        await state.set_state(InvoiceStates.waiting_confirmation)


@router.message(InvoiceStates.editing_invoice_number)
async def process_invoice_num_edit(message: Message, state: FSMContext):
    """Process invoice number edit."""
    data = await state.get_data()
    invoice = data.get("invoice_data")
    
    if invoice:
        invoice.invoice_number = message.text
        await state.update_data(invoice_data=invoice)
        await update_invoice_in_place(message, state, "✅ تم تحديث رقم الفاتورة")
        await state.set_state(InvoiceStates.waiting_confirmation)


@router.message(InvoiceStates.editing_tax_number)
async def process_tax_num_edit(message: Message, state: FSMContext):
    """Process tax number edit."""
    data = await state.get_data()
    invoice = data.get("invoice_data")
    
    if invoice:
        invoice.tax_number = message.text
        await state.update_data(invoice_data=invoice)
        await update_invoice_in_place(message, state, "✅ تم تحديث الرقم الضريبي")
        await state.set_state(InvoiceStates.waiting_confirmation)


@router.message(InvoiceStates.editing_discount)
async def process_discount_edit(message: Message, state: FSMContext):
    """Process discount edit."""
    try:
        new_value = float(message.text)
        data = await state.get_data()
        invoice = data.get("invoice_data")
        
        if invoice:
            invoice.discount = new_value
            recalculate_invoice(invoice)
            await state.update_data(invoice_data=invoice)
            await update_invoice_in_place(message, state, "✅ تم تحديث الخصم")
            await state.set_state(InvoiceStates.waiting_confirmation)
    except ValueError:
        await message.answer("❌ قيمة غير صحيحة. أدخل رقماً.")


@router.message(InvoiceStates.editing_tax_rate)
async def process_tax_rate_edit(message: Message, state: FSMContext):
    """Process tax rate edit."""
    try:
        new_value = float(message.text)
        data = await state.get_data()
        invoice = data.get("invoice_data")
        
        if invoice:
            invoice.tax_rate = new_value
            recalculate_invoice(invoice)
            await state.update_data(invoice_data=invoice)
            await update_invoice_in_place(message, state, f"✅ تم تحديث الضريبة إلى {new_value}%")
            await state.set_state(InvoiceStates.waiting_confirmation)
    except ValueError:
        await message.answer("❌ قيمة غير صحيحة. أدخل رقماً.")
