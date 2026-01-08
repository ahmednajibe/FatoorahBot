"""
Item Edit Handlers
Callback and message handlers for editing invoice items - in-place updates
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.invoice_keyboard import get_items_list_keyboard, get_item_edit_keyboard, get_edit_menu_keyboard
from bot.states.invoice_states import InvoiceStates
from bot.handlers.invoice import format_invoice_result
from utils.calculations import recalculate_invoice

logger = logging.getLogger(__name__)
router = Router()


async def update_invoice_in_place(message: Message, state: FSMContext, success_text: str = "✅ تم التحديث"):
    """Update the original invoice message in-place."""
    data = await state.get_data()
    invoice = data.get("invoice_data")
    message_id = data.get("message_id")
    
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
            
            # Send quick confirmation
            await message.answer(success_text)
            
        except Exception as e:
            logger.error(f"Failed to update message: {e}")
            await message.answer("❌ حدث خطأ أثناء التحديث")


@router.callback_query(F.data == "edit_items")
async def edit_items_callback(callback: CallbackQuery, state: FSMContext):
    """Show list of items to edit."""
    await callback.answer()
    
    data = await state.get_data()
    invoice = data.get("invoice_data")
    
    if not invoice or not invoice.items:
        await callback.answer("لا توجد أصناف للتعديل", show_alert=True)
        return
    
    # Edit the current message to show items list
    await callback.message.edit_reply_markup(
        reply_markup=get_items_list_keyboard(len(invoice.items))
    )


@router.callback_query(F.data.startswith("select_item_"))
async def select_item_callback(callback: CallbackQuery, state: FSMContext):
    """Show edit options for selected item."""
    await callback.answer()
    
    item_index = int(callback.data.split("_")[-1])
    data = await state.get_data()
    invoice = data.get("invoice_data")
    
    if not invoice or item_index >= len(invoice.items):
        await callback.answer("خطأ في تحديد الصنف", show_alert=True)
        return
    
    item = invoice.items[item_index]
    
    # Show item details with edit options
    await callback.message.edit_reply_markup(
        reply_markup=get_item_edit_keyboard(item_index)
    )
    await callback.answer(
        f"📦 {item.name}\nالكمية: {item.quantity} | السعر: {item.unit_price}",
        show_alert=True
    )


@router.callback_query(F.data.startswith("edit_item_name_"))
async def edit_item_name_callback(callback: CallbackQuery, state: FSMContext):
    """Start editing item name."""
    await callback.answer()
    item_index = int(callback.data.split("_")[-1])
    
    msg = await callback.message.answer("📝 ادخل اسم الصنف الجديد:")
    await state.update_data(editing_item_index=item_index, prompt_message_id=msg.message_id)
    await state.set_state(InvoiceStates.editing_item_name)


@router.callback_query(F.data.startswith("edit_item_qty_"))
async def edit_item_qty_callback(callback: CallbackQuery, state: FSMContext):
    """Start editing item quantity."""
    await callback.answer()
    item_index = int(callback.data.split("_")[-1])
    
    msg = await callback.message.answer("📝 ادخل الكمية الجديدة:")
    await state.update_data(editing_item_index=item_index, prompt_message_id=msg.message_id)
    await state.set_state(InvoiceStates.editing_item_quantity)


@router.callback_query(F.data.startswith("edit_item_unit_"))
async def edit_item_unit_callback(callback: CallbackQuery, state: FSMContext):
    """Start editing item unit."""
    await callback.answer()
    item_index = int(callback.data.split("_")[-1])
    
    msg = await callback.message.answer("📝 ادخل الوحدة الجديدة:")
    await state.update_data(editing_item_index=item_index, prompt_message_id=msg.message_id)
    await state.set_state(InvoiceStates.editing_item_unit)


@router.callback_query(F.data.startswith("edit_item_price_"))
async def edit_item_price_callback(callback: CallbackQuery, state: FSMContext):
    """Start editing item price."""
    await callback.answer()
    item_index = int(callback.data.split("_")[-1])
    
    msg = await callback.message.answer("📝 ادخل سعر الوحدة الجديد:")
    await state.update_data(editing_item_index=item_index, prompt_message_id=msg.message_id)
    await state.set_state(InvoiceStates.editing_item_price)


@router.callback_query(F.data.startswith("delete_item_"))
async def delete_item_callback(callback: CallbackQuery, state: FSMContext):
    """Delete an item from invoice."""
    item_index = int(callback.data.split("_")[-1])
    
    data = await state.get_data()
    invoice = data.get("invoice_data")
    message_id = data.get("message_id")
    
    if not invoice or item_index >= len(invoice.items):
        await callback.answer("خطأ في حذف الصنف", show_alert=True)
        return
    
    deleted_item = invoice.items.pop(item_index)
    recalculate_invoice(invoice)
    await state.update_data(invoice_data=invoice)
    
    # Update invoice message in-place
    result_text = format_invoice_result(invoice)
    try:
        await callback.message.edit_text(
            text=result_text,
            parse_mode="MarkdownV2",
            reply_markup=get_edit_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Failed to update message: {e}")
    
    await callback.answer(f"✅ تم حذف: {deleted_item.name}", show_alert=True)
    await state.set_state(InvoiceStates.waiting_confirmation)


# Message handlers for item editing

@router.message(InvoiceStates.editing_item_name)
async def process_item_name_edit(message: Message, state: FSMContext):
    """Process item name edit."""
    data = await state.get_data()
    invoice = data.get("invoice_data")
    item_index = data.get("editing_item_index")
    
    if invoice and item_index is not None and item_index < len(invoice.items):
        invoice.items[item_index].name = message.text
        await state.update_data(invoice_data=invoice)
        await update_invoice_in_place(message, state, "✅ تم تحديث اسم الصنف")
        await state.set_state(InvoiceStates.waiting_confirmation)


@router.message(InvoiceStates.editing_item_quantity)
async def process_item_qty_edit(message: Message, state: FSMContext):
    """Process item quantity edit."""
    try:
        new_value = float(message.text)
        data = await state.get_data()
        invoice = data.get("invoice_data")
        item_index = data.get("editing_item_index")
        
        if invoice and item_index is not None and item_index < len(invoice.items):
            invoice.items[item_index].quantity = new_value
            recalculate_invoice(invoice)
            await state.update_data(invoice_data=invoice)
            await update_invoice_in_place(message, state, "✅ تم تحديث الكمية")
            await state.set_state(InvoiceStates.waiting_confirmation)
    except ValueError:
        await message.answer("❌ قيمة غير صحيحة. أدخل رقماً.")


@router.message(InvoiceStates.editing_item_unit)
async def process_item_unit_edit(message: Message, state: FSMContext):
    """Process item unit edit."""
    data = await state.get_data()
    invoice = data.get("invoice_data")
    item_index = data.get("editing_item_index")
    
    if invoice and item_index is not None and item_index < len(invoice.items):
        invoice.items[item_index].unit = message.text
        await state.update_data(invoice_data=invoice)
        await update_invoice_in_place(message, state, "✅ تم تحديث الوحدة")
        await state.set_state(InvoiceStates.waiting_confirmation)


@router.message(InvoiceStates.editing_item_price)
async def process_item_price_edit(message: Message, state: FSMContext):
    """Process item price edit."""
    try:
        new_value = float(message.text)
        data = await state.get_data()
        invoice = data.get("invoice_data")
        item_index = data.get("editing_item_index")
        
        if invoice and item_index is not None and item_index < len(invoice.items):
            invoice.items[item_index].unit_price = new_value
            recalculate_invoice(invoice)
            await state.update_data(invoice_data=invoice)
            await update_invoice_in_place(message, state, "✅ تم تحديث السعر")
            await state.set_state(InvoiceStates.waiting_confirmation)
    except ValueError:
        await message.answer("❌ قيمة غير صحيحة. أدخل رقماً.")
