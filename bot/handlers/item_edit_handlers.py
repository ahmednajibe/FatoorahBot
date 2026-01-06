"""
Item Edit Handlers
Callback and message handlers for editing invoice items
"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from bot.keyboards.invoice_keyboard import get_items_list_keyboard, get_item_edit_keyboard, get_edit_menu_keyboard
from bot.states.invoice_states import InvoiceStates
from bot.handlers.edit_handlers import update_invoice_display
from utils.calculations import recalculate_invoice

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "edit_items")
async def edit_items_callback(callback: CallbackQuery, state: FSMContext):
    """Show list of items to edit."""
    await callback.answer()
    
    data = await state.get_data()
    invoice = data.get("invoice_data")
    
    if not invoice or not invoice.items:
        await callback.answer("لا توجد أصناف للتعديل", show_alert=True)
        return
    
    await callback.message.reply(
        f"📦 *الأصناف \\({len(invoice.items)}\\):*\n\n"
        "اختر الصنف الذي تريد تعديله:",
        parse_mode="MarkdownV2",
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
    
    await callback.message.reply(
        f"📦 *الصنف {item_index + 1}:*\n\n"
        f"الاسم: {item.name}\n"
        f"الكمية: {item.quantity}\n"
        f"الوحدة: {item.unit}\n"
        f"سعر الوحدة: {item.unit_price}\n"
        f"الإجمالي: {item.total}",
        reply_markup=get_item_edit_keyboard(item_index)
    )


@router.callback_query(F.data.startswith("edit_item_name_"))
async def edit_item_name_callback(callback: CallbackQuery, state: FSMContext):
    """Start editing item name."""
    await callback.answer()
    item_index = int(callback.data.split("_")[-1])
    
    await state.update_data(editing_item_index=item_index)
    await state.set_state(InvoiceStates.editing_item_name)
    await callback.message.reply("📝 ادخل اسم الصنف الجديد:")


@router.callback_query(F.data.startswith("edit_item_qty_"))
async def edit_item_qty_callback(callback: CallbackQuery, state: FSMContext):
    """Start editing item quantity."""
    await callback.answer()
    item_index = int(callback.data.split("_")[-1])
    
    await state.update_data(editing_item_index=item_index)
    await state.set_state(InvoiceStates.editing_item_quantity)
    await callback.message.reply("📝 ادخل الكمية الجديدة:")


@router.callback_query(F.data.startswith("edit_item_unit_"))
async def edit_item_unit_callback(callback: CallbackQuery, state: FSMContext):
    """Start editing item unit."""
    await callback.answer()
    item_index = int(callback.data.split("_")[-1])
    
    await state.update_data(editing_item_index=item_index)
    await state.set_state(InvoiceStates.editing_item_unit)
    await callback.message.reply("📝 ادخل الوحدة الجديدة:")


@router.callback_query(F.data.startswith("edit_item_price_"))
async def edit_item_price_callback(callback: CallbackQuery, state: FSMContext):
    """Start editing item price."""
    await callback.answer()
    item_index = int(callback.data.split("_")[-1])
    
    await state.update_data(editing_item_index=item_index)
    await state.set_state(InvoiceStates.editing_item_price)
    await callback.message.reply("📝 ادخل سعر الوحدة الجديد:")


@router.callback_query(F.data.startswith("edit_item_total_"))
async def edit_item_total_callback(callback: CallbackQuery, state: FSMContext):
    """Start editing item total."""
    await callback.answer()
    item_index = int(callback.data.split("_")[-1])
    
    await state.update_data(editing_item_index=item_index)
    await state.set_state(InvoiceStates.editing_item_total)
    await callback.message.reply("📝 ادخل إجمالي الصنف الجديد:")


@router.callback_query(F.data.startswith("delete_item_"))
async def delete_item_callback(callback: CallbackQuery, state: FSMContext):
    """Delete an item from invoice."""
    await callback.answer()
    item_index = int(callback.data.split("_")[-1])
    
    data = await state.get_data()
    invoice = data.get("invoice_data")
    
    if not invoice or item_index >= len(invoice.items):
        await callback.answer("خطأ في حذف الصنف", show_alert=True)
        return
    
    deleted_item = invoice.items.pop(item_index)
    
    # Recalculate totals
    recalculate_invoice(invoice)
    
    await state.update_data(invoice_data=invoice)
    
    await callback.message.reply(f"✅ تم حذف الصنف: {deleted_item.name}")
    await update_invoice_display(callback.message, state)
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
        await message.answer("✅ تم تحديث اسم الصنف")
        await update_invoice_display(message, state)
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
            
            # Recalculate totals
            recalculate_invoice(invoice)
            
            await state.update_data(invoice_data=invoice)
            await message.answer("✅ تم تحديث الكمية")
            await update_invoice_display(message, state)
            await state.set_state(InvoiceStates.waiting_confirmation)
    except ValueError:
        await message.answer("❌ قيمة غير صحيحة. أدخل رقماً صحيحاً.")


@router.message(InvoiceStates.editing_item_unit)
async def process_item_unit_edit(message: Message, state: FSMContext):
    """Process item unit edit."""
    data = await state.get_data()
    invoice = data.get("invoice_data")
    item_index = data.get("editing_item_index")
    
    if invoice and item_index is not None and item_index < len(invoice.items):
        invoice.items[item_index].unit = message.text
        await state.update_data(invoice_data=invoice)
        await message.answer("✅ تم تحديث الوحدة")
        await update_invoice_display(message, state)
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
            
            # Recalculate totals
            recalculate_invoice(invoice)
            
            await state.update_data(invoice_data=invoice)
            await message.answer("✅ تم تحديث سعر الوحدة")
            await update_invoice_display(message, state)
            await state.set_state(InvoiceStates.waiting_confirmation)
    except ValueError:
        await message.answer("❌ قيمة غير صحيحة. أدخل رقماً صحيحاً.")


@router.message(InvoiceStates.editing_item_total)
async def process_item_total_edit(message: Message, state: FSMContext):
    """Process item total edit."""
    try:
        new_value = float(message.text)
        data = await state.get_data()
        invoice = data.get("invoice_data")
        item_index = data.get("editing_item_index")
        
        if invoice and item_index is not None and item_index < len(invoice.items):
            invoice.items[item_index].total = new_value
            await state.update_data(invoice_data=invoice)
            await message.answer("✅ تم تحديث إجمالي الصنف")
            await update_invoice_display(message, state)
            await state.set_state(InvoiceStates.waiting_confirmation)
    except ValueError:
        await message.answer("❌ قيمة غير صحيحة. أدخل رقماً صحيحاً.")
