"""
Menu Callback Handlers
Handles main menu button clicks
"""
import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from services.database import db_service
from services.export_generator import export_generator
from bot.handlers.start import get_main_menu_keyboard, get_invoices_menu_keyboard, get_items_menu_keyboard

logger = logging.getLogger(__name__)
router = Router()


class DateInputStates(StatesGroup):
    """States for date input."""
    waiting_invoices_date = State()
    waiting_items_date = State()


@router.callback_query(F.data == "menu_main")
async def menu_main_callback(callback: CallbackQuery, state: FSMContext):
    """Show main menu."""
    await callback.answer()
    await state.clear()
    await callback.message.edit_text(
        "📋 القائمة الرئيسية\n\n"
        "اختر ما تريد:",
        reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(F.data == "menu_invoices")
async def menu_invoices_callback(callback: CallbackQuery):
    """Show invoices export menu."""
    await callback.answer()
    await callback.message.edit_text(
        "📊 تقارير الفواتير\n\n"
        "اختر نوع التقرير:",
        reply_markup=get_invoices_menu_keyboard()
    )


@router.callback_query(F.data == "menu_items")
async def menu_items_callback(callback: CallbackQuery):
    """Show items export menu."""
    await callback.answer()
    await callback.message.edit_text(
        "📦 تقارير الأصناف\n\n"
        "اختر نوع التقرير:",
        reply_markup=get_items_menu_keyboard()
    )


@router.callback_query(F.data == "menu_stats")
async def menu_stats_callback(callback: CallbackQuery):
    """Show user statistics."""
    await callback.answer()
    user_id = callback.from_user.id
    
    try:
        invoice_count = db_service.get_invoice_count(user_id)
        await callback.message.edit_text(
            f"📈 إحصائياتك\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📊 عدد الفواتير المحفوظة: {invoice_count}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 الأوامر المتاحة:\n\n"
            f"    /export_invoices - كل الفواتير\n"
            f"    /export_items - كل الأصناف\n"
            f"    /stats - هذه الصفحة",
            reply_markup=get_main_menu_keyboard()
        )
    except Exception as e:
        logger.error(f"Failed to show stats: {e}")
        await callback.message.reply("❌ حدث خطأ")


@router.callback_query(F.data == "menu_help")
async def menu_help_callback(callback: CallbackQuery):
    """Show help information."""
    await callback.answer()
    await callback.message.edit_text(
        "❓ المساعدة\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📸 كيف تستخدم البوت:\n\n"
        "    1️⃣ أرسل صورة فاتورة\n"
        "    2️⃣ راجع البيانات المستخرجة\n"
        "    3️⃣ عدّل إذا لزم الأمر\n"
        "    4️⃣ اضغط حفظ\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📊 التقارير:\n\n"
        "    • اضغط 'تقارير الفواتير' لتصدير الفواتير\n"
        "    • اضغط 'تقارير الأصناف' لتصدير الأصناف\n"
        "    • يمكنك التصدير لفترة محددة",
        reply_markup=get_main_menu_keyboard()
    )


# Export handlers

@router.callback_query(F.data == "export_all_invoices")
async def export_all_invoices_callback(callback: CallbackQuery):
    """Export all invoices - sends Excel directly."""
    await callback.answer("⏳ جاري إنشاء التقرير...")
    user_id = callback.from_user.id
    
    try:
        invoices = db_service.get_user_invoices(user_id)
        
        if not invoices:
            await callback.answer("❌ لا توجد فواتير", show_alert=True)
            return
        
        invoices_list = [dict(inv) for inv in invoices]
        excel_file = export_generator.generate_invoices_report(invoices_list)
        filename = f"invoices_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        await callback.message.answer_document(
            document=BufferedInputFile(excel_file.read(), filename=filename),
            caption=f"📊 تقرير الفواتير - عدد: {len(invoices)}"
        )
        
        logger.info(f"User {user_id} exported {len(invoices)} invoices")
        
    except Exception as e:
        logger.error(f"Failed to export invoices: {e}")
        await callback.answer("❌ حدث خطأ", show_alert=True)


@router.callback_query(F.data == "export_invoices_date")
async def export_invoices_date_callback(callback: CallbackQuery, state: FSMContext):
    """Ask for date range for invoices."""
    await callback.answer()
    await callback.message.reply(
        "📅 أدخل الفترة بهذا الشكل:\n\n"
        "YYYY-MM-DD YYYY-MM-DD\n\n"
        "مثال:\n"
        "2024-01-01 2024-12-31"
    )
    await state.set_state(DateInputStates.waiting_invoices_date)


@router.callback_query(F.data == "export_all_items")
async def export_all_items_callback(callback: CallbackQuery):
    """Export all items - sends Excel directly."""
    await callback.answer("⏳ جاري إنشاء التقرير...")
    user_id = callback.from_user.id
    
    try:
        items = db_service.get_user_items(user_id)
        
        if not items:
            await callback.answer("❌ لا توجد أصناف", show_alert=True)
            return
        
        items_list = [dict(item) for item in items]
        excel_file = export_generator.generate_items_report(items_list)
        filename = f"items_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        await callback.message.answer_document(
            document=BufferedInputFile(excel_file.read(), filename=filename),
            caption=f"📦 تقرير الأصناف - عدد: {len(items)}"
        )
        
        logger.info(f"User {user_id} exported {len(items)} items")
        
    except Exception as e:
        logger.error(f"Failed to export items: {e}")
        await callback.answer("❌ حدث خطأ", show_alert=True)


@router.callback_query(F.data == "export_items_date")
async def export_items_date_callback(callback: CallbackQuery, state: FSMContext):
    """Ask for date range for items."""
    await callback.answer()
    await callback.message.reply(
        "📅 أدخل الفترة بهذا الشكل:\n\n"
        "YYYY-MM-DD YYYY-MM-DD\n\n"
        "مثال:\n"
        "2024-01-01 2024-12-31"
    )
    await state.set_state(DateInputStates.waiting_items_date)


# Date input handlers

@router.message(DateInputStates.waiting_invoices_date)
async def process_invoices_date(message, state: FSMContext):
    """Process date input for invoices export."""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ صيغة خاطئة. أدخل تاريخين مثال: 2024-01-01 2024-12-31")
            return
        
        start_date, end_date = parts[0], parts[1]
        user_id = message.from_user.id
        
        invoices = db_service.get_user_invoices(user_id, start_date, end_date)
        
        if not invoices:
            await message.answer(f"❌ لا توجد فواتير في الفترة من {start_date} إلى {end_date}")
            await state.clear()
            return
        
        invoices_list = [dict(inv) for inv in invoices]
        
        await message.answer("⏳ جاري إنشاء التقرير...")
        excel_file = export_generator.generate_invoices_report(invoices_list)
        filename = f"invoices_{start_date}_to_{end_date}.xlsx"
        
        await message.answer_document(
            document=BufferedInputFile(excel_file.read(), filename=filename),
            caption=f"📊 تقرير الفواتير\n\nالفترة: {start_date} إلى {end_date}\nعدد الفواتير: {len(invoices)}"
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Failed to export invoices by date: {e}")
        await message.answer("❌ حدث خطأ. تأكد من صيغة التاريخ")
        await state.clear()


@router.message(DateInputStates.waiting_items_date)
async def process_items_date(message, state: FSMContext):
    """Process date input for items export."""
    try:
        parts = message.text.split()
        if len(parts) < 2:
            await message.answer("❌ صيغة خاطئة. أدخل تاريخين مثال: 2024-01-01 2024-12-31")
            return
        
        start_date, end_date = parts[0], parts[1]
        user_id = message.from_user.id
        
        items = db_service.get_user_items(user_id, start_date, end_date)
        
        if not items:
            await message.answer(f"❌ لا توجد أصناف في الفترة من {start_date} إلى {end_date}")
            await state.clear()
            return
        
        items_list = [dict(item) for item in items]
        
        await message.answer("⏳ جاري إنشاء التقرير...")
        excel_file = export_generator.generate_items_report(items_list)
        filename = f"items_{start_date}_to_{end_date}.xlsx"
        
        await message.answer_document(
            document=BufferedInputFile(excel_file.read(), filename=filename),
            caption=f"📦 تقرير الأصناف\n\nالفترة: {start_date} إلى {end_date}\nعدد الأصناف: {len(items)}"
        )
        
        await state.clear()
        
    except Exception as e:
        logger.error(f"Failed to export items by date: {e}")
        await message.answer("❌ حدث خطأ. تأكد من صيغة التاريخ")
        await state.clear()
