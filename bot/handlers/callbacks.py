"""
Callback Handlers
Handles button clicks for invoice confirmation and editing
"""
import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext

from services.database import db_service
from services.excel_generator import excel_generator
from bot.keyboards.invoice_keyboard import get_edit_menu_keyboard, get_totals_edit_keyboard, get_invoice_confirmation_keyboard
from bot.states.invoice_states import InvoiceStates
from models.invoice import InvoiceData

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "invoice_save")
async def save_invoice_callback(callback: CallbackQuery, state: FSMContext):
    """Save invoice to database and send Excel."""
    await callback.answer()
    
    # Get stored invoice data
    data = await state.get_data()
    invoice = data.get("invoice_data")
    
    if not invoice:
        await callback.message.edit_text("❌ خطأ: لم يتم العثور على بيانات الفاتورة")
        await state.clear()
        return
    
    try:
        # Save to database
        user_id = callback.from_user.id
        invoice_id = db_service.save_invoice(user_id, invoice)
        
        # Remove buttons and add saved message
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.reply(
            f"✅ تم حفظ الفاتورة بنجاح!\n\n"
            f"📊 عدد الفواتير المحفوظة: {db_service.get_invoice_count(user_id)}\n\n"
            f"💡 استخدم /stats لعرض الإحصائيات والتقارير"
        )
        
        logger.info(f"Invoice {invoice_id} saved for user {user_id}")
        
    except Exception as e:
        logger.error(f"Failed to save invoice: {e}")
        await callback.message.reply("❌ حدث خطأ أثناء حفظ الفاتورة")
    
    await state.clear()


@router.callback_query(F.data == "invoice_edit")
async def edit_invoice_callback(callback: CallbackQuery, state: FSMContext):
    """Show edit menu."""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=get_edit_menu_keyboard())


@router.callback_query(F.data == "invoice_cancel")
async def cancel_invoice_callback(callback: CallbackQuery, state: FSMContext):
    """Cancel invoice without saving - delete all related messages."""
    await callback.answer("تم الإلغاء")
    
    # Get stored message IDs
    data = await state.get_data()
    photo_message_id = data.get("photo_message_id")
    
    try:
        # Delete original photo message
        if photo_message_id:
            await callback.bot.delete_message(
                chat_id=callback.message.chat.id,
                message_id=photo_message_id
            )
        
        # Delete invoice data message
        await callback.message.delete()
        
        # Send cancellation confirmation
        await callback.bot.send_message(
            chat_id=callback.message.chat.id,
            text="❌ تم إلغاء الفاتورة ومسح جميع الرسائل المتعلقة بها"
        )
    except Exception as e:
        logger.error(f"Failed to delete messages: {e}")
        await callback.message.reply("❌ تم إلغاء الفاتورة")
    
    await state.clear()


@router.callback_query(F.data == "edit_supplier")
async def edit_supplier_callback(callback: CallbackQuery, state: FSMContext):
    """Start editing supplier name."""
    await callback.answer()
    await callback.message.reply("📝 أدخل اسم المورد الجديد:")
    await state.set_state(InvoiceStates.editing_supplier)


@router.callback_query(F.data == "edit_date")
async def edit_date_callback(callback: CallbackQuery, state: FSMContext):
    """Start editing date."""
    await callback.answer()
    await callback.message.reply("📅 أدخل التاريخ الجديد (YYYY-MM-DD):")
    await state.set_state(InvoiceStates.editing_date)


@router.callback_query(F.data == "edit_invoice_num")
async def edit_invoice_num_callback(callback: CallbackQuery, state: FSMContext):
    """Start editing invoice number."""
    await callback.answer()
    await callback.message.reply("📄 أدخل رقم الفاتورة الجديد:")
    await state.set_state(InvoiceStates.editing_invoice_number)


@router.callback_query(F.data == "edit_tax_num")
async def edit_tax_num_callback(callback: CallbackQuery, state: FSMContext):
    """Start editing tax number."""
    await callback.answer()
    await callback.message.reply("🔢 أدخل الرقم الضريبي الجديد:")
    await state.set_state(InvoiceStates.editing_tax_number)


@router.callback_query(F.data == "edit_totals")
async def edit_totals_callback(callback: CallbackQuery, state: FSMContext):
    """Show totals edit menu."""
    await callback.answer()
    await callback.message.edit_reply_markup(reply_markup=get_totals_edit_keyboard())


@router.callback_query(F.data == "edit_subtotal")
async def edit_subtotal_callback(callback: CallbackQuery, state: FSMContext):
    """Start editing subtotal."""
    await callback.answer()
    await callback.message.reply("💰 أدخل المجموع الفرعي الجديد:")
    await state.set_state(InvoiceStates.editing_subtotal)


@router.callback_query(F.data == "edit_discount")
async def edit_discount_callback(callback: CallbackQuery, state: FSMContext):
    """Start editing discount."""
    await callback.answer()
    await callback.message.reply("💵 أدخل الخصم الجديد:")
    await state.set_state(InvoiceStates.editing_discount)


@router.callback_query(F.data == "edit_tax_rate")
async def edit_tax_rate_callback(callback: CallbackQuery, state: FSMContext):
    """Start editing tax rate."""
    await callback.answer()
    await callback.message.reply("📊 أدخل نسبة الضريبة الجديدة (مثال: 15 لـ 15%):")
    await state.set_state(InvoiceStates.editing_tax_rate)
