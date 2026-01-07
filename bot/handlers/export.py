"""
Export Commands
Commands for exporting invoices and items to Excel
"""
import logging
from datetime import datetime
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, BufferedInputFile
from aiogram.fsm.context import FSMContext

from services.database import db_service
from services.export_generator import export_generator

logger = logging.getLogger(__name__)
router = Router()


@router.message(Command("export_invoices"))
async def export_all_invoices(message: Message, state: FSMContext):
    """Export all user's invoices to Excel."""
    user_id = message.from_user.id
    
    # Clear any active state
    await state.clear()
    
    try:
        # Get all invoices
        invoices = db_service.get_user_invoices(user_id)
        
        if not invoices:
            await message.answer("❌ لا توجد فواتير محفوظة")
            return
        
        # Convert to list of dicts
        invoices_list = [dict(inv) for inv in invoices]
        
        # Generate Excel
        await message.answer("⏳ جاري إنشاء التقرير...")
        excel_file = export_generator.generate_invoices_report(invoices_list)
        filename = f"invoices_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Send file
        await message.answer_document(
            document=BufferedInputFile(excel_file.read(), filename=filename),
            caption=f"📊 تقرير الفواتير\n\nعدد الفواتير: {len(invoices)}"
        )
        
        logger.info(f"User {user_id} exported {len(invoices)} invoices")
        
    except Exception as e:
        logger.error(f"Failed to export invoices: {e}")
        await message.answer("❌ حدث خطأ أثناء إنشاء التقرير")


@router.message(Command("export_invoices_date"))
async def export_invoices_by_date(message: Message, state: FSMContext):
    """Export invoices filtered by date range."""
    user_id = message.from_user.id
    await state.clear()
    
    # Parse command arguments
    args = message.text.split()
    
    if len(args) < 3:
        await message.answer(
            "📅 *استخدام الأمر:*\n\n"
            "`/export_invoices_date YYYY-MM-DD YYYY-MM-DD`\n\n"
            "مثال:\n"
            "`/export_invoices_date 2024-01-01 2024-12-31`",
            parse_mode="Markdown"
        )
        return
    
    start_date = args[1]
    end_date = args[2]
    
    try:
        # Get filtered invoices
        invoices = db_service.get_user_invoices(user_id, start_date, end_date)
        
        if not invoices:
            await message.answer(f"❌ لا توجد فواتير في الفترة من {start_date} إلى {end_date}")
            return
        
        # Convert to list of dicts
        invoices_list = [dict(inv) for inv in invoices]
        
        # Generate Excel
        await message.answer("⏳ جاري إنشاء التقرير...")
        excel_file = export_generator.generate_invoices_report(invoices_list)
        filename = f"invoices_{start_date}_to_{end_date}.xlsx"
        
        # Send file
        await message.answer_document(
            document=BufferedInputFile(excel_file.read(), filename=filename),
            caption=f"📊 تقرير الفواتير\n\nالفترة: {start_date} إلى {end_date}\nعدد الفواتير: {len(invoices)}"
        )
        
        logger.info(f"User {user_id} exported {len(invoices)} invoices from {start_date} to {end_date}")
        
    except Exception as e:
        logger.error(f"Failed to export invoices by date: {e}")
        await message.answer("❌ حدث خطأ. تأكد من صيغة التاريخ (YYYY-MM-DD)")


@router.message(Command("export_items"))
async def export_all_items(message: Message, state: FSMContext):
    """Export all user's items to Excel."""
    user_id = message.from_user.id
    await state.clear()
    
    try:
        # Get all items
        items = db_service.get_user_items(user_id)
        
        if not items:
            await message.answer("❌ لا توجد أصناف محفوظة")
            return
        
        # Convert to list of dicts
        items_list = [dict(item) for item in items]
        
        # Generate Excel
        await message.answer("⏳ جاري إنشاء التقرير...")
        excel_file = export_generator.generate_items_report(items_list)
        filename = f"items_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        
        # Send file
        await message.answer_document(
            document=BufferedInputFile(excel_file.read(), filename=filename),
            caption=f"📦 تقرير الأصناف\n\nعدد الأصناف: {len(items)}"
        )
        
        logger.info(f"User {user_id} exported {len(items)} items")
        
    except Exception as e:
        logger.error(f"Failed to export items: {e}")
        await message.answer("❌ حدث خطأ أثناء إنشاء التقرير")


@router.message(Command("export_items_date"))
async def export_items_by_date(message: Message, state: FSMContext):
    """Export items filtered by date range."""
    user_id = message.from_user.id
    await state.clear()
    
    # Parse command arguments
    args = message.text.split()
    
    if len(args) < 3:
        await message.answer(
            "📅 *استخدام الأمر:*\n\n"
            "`/export_items_date YYYY-MM-DD YYYY-MM-DD`\n\n"
            "مثال:\n"
            "`/export_items_date 2024-01-01 2024-12-31`",
            parse_mode="Markdown"
        )
        return
    
    start_date = args[1]
    end_date = args[2]
    
    try:
        # Get filtered items
        items = db_service.get_user_items(user_id, start_date, end_date)
        
        if not items:
            await message.answer(f"❌ لا توجد أصناف في الفترة من {start_date} إلى {end_date}")
            return
        
        # Convert to list of dicts
        items_list = [dict(item) for item in items]
        
        # Generate Excel
        await message.answer("⏳ جاري إنشاء التقرير...")
        excel_file = export_generator.generate_items_report(items_list)
        filename = f"items_{start_date}_to_{end_date}.xlsx"
        
        # Send file
        await message.answer_document(
            document=BufferedInputFile(excel_file.read(), filename=filename),
            caption=f"📦 تقرير الأصناف\n\nالفترة: {start_date} إلى {end_date}\nعدد الأصناف: {len(items)}"
        )
        
        logger.info(f"User {user_id} exported {len(items)} items from {start_date} to {end_date}")
        
    except Exception as e:
        logger.error(f"Failed to export items by date: {e}")
        await message.answer("❌ حدث خطأ. تأكد من صيغة التاريخ (YYYY-MM-DD)")


@router.message(Command("stats"))
async def show_stats(message: Message, state: FSMContext):
    """Show user statistics with export buttons."""
    user_id = message.from_user.id
    await state.clear()
    
    try:
        invoice_count = db_service.get_invoice_count(user_id)
        
        # Create export buttons keyboard
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 كل الفواتير", callback_data="export_all_invoices"),
                InlineKeyboardButton(text="📅 فواتير بتاريخ", callback_data="export_invoices_date")
            ],
            [
                InlineKeyboardButton(text="📦 كل الأصناف", callback_data="export_all_items"),
                InlineKeyboardButton(text="📅 أصناف بتاريخ", callback_data="export_items_date")
            ]
        ])
        
        await message.answer(
            f"📊 إحصائياتك:\n\n"
            f"عدد الفواتير المحفوظة: {invoice_count}\n\n"
            f"💡 اختر نوع التقرير:",
            reply_markup=keyboard
        )
    except Exception as e:
        logger.error(f"Failed to show stats: {e}")
        await message.answer("❌ حدث خطأ")
