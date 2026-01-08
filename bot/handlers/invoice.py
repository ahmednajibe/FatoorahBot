"""
Invoice Handler
Handles invoice images and PDF files
"""
import logging
from datetime import datetime
from aiogram import Router, F, Bot
from aiogram.types import Message, BufferedInputFile, CallbackQuery
from aiogram.fsm.context import FSMContext

from services.ocr_service import ocr_service
from services.validator import validator
from services.excel_generator import excel_generator
from services.database import db_service
from bot.keyboards.invoice_keyboard import get_invoice_confirmation_keyboard, get_edit_menu_keyboard, get_totals_edit_keyboard, get_duplicate_warning_keyboard
from bot.states.invoice_states import InvoiceStates

logger = logging.getLogger(__name__)
router = Router()


def format_invoice_result(invoice) -> str:
    """Format invoice data for display."""
    
    # Escape special characters for MarkdownV2
    def escape(text):
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        for char in special_chars:
            text = str(text).replace(char, f'\\{char}')
        return text
    
    lines = [
        "✅  *تم تحليل الفاتورة بنجاح\\!*",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "",
        "📋  *بيانات الفاتورة:*",
        "",
        f"    🏢  المورد: {escape(invoice.supplier_name or 'غير محدد')}",
        f"    🔢  الرقم الضريبي: {escape(invoice.tax_number or 'غير محدد')}",
        f"    📄  رقم الفاتورة: {escape(invoice.invoice_number or 'غير محدد')}",
        f"    📅  التاريخ: {escape(invoice.invoice_date or 'غير محدد')}",
        "",
        "━━━━━━━━━━━━━━━━━━━━",
        "",
        "🛒  *الأصناف:*",
        "",
    ]
    
    for i, item in enumerate(invoice.items, 1):
        lines.append(f"    {i}\\. {escape(item.name)}")
        lines.append(f"        الكمية: {escape(item.quantity)} {escape(item.unit)}")
        lines.append(f"        السعر: {escape(item.unit_price)}")
        lines.append(f"        الإجمالي: {escape(item.total)}")
        lines.append("")
    
    lines.extend([
        "━━━━━━━━━━━━━━━━━━━━",
        "",
        "💰  *الإجماليات:*",
        "",
        f"    المجموع الفرعي: {escape(invoice.subtotal)}",
        f"    الخصم: {escape(invoice.discount)}",
        f"    الضريبة \\({escape(invoice.tax_rate)}%\\): {escape(invoice.tax_amount)}",
        f"    *الإجمالي النهائي: {escape(invoice.total_amount)}*",
    ])

    # Add validation message if present
    if invoice.validation_message:
        lines.extend([
            "",
            "━━━━━━━━━━━━━━━━━━━━",
            "",
            "📊  *التدقيق الحسابي:*",
        "",
        f"    {escape(invoice.validation_message)}",
    ])
    
    return "\n".join(lines)


@router.message(F.photo)
async def handle_photo(message: Message, bot: Bot, state: FSMContext) -> None:
    """Handle incoming photo messages."""
    
    # Send processing message
    processing_msg = await message.answer(
        "⏳  *جاري تحليل الفاتورة\\.\\.\\.*\n\n"
        "🔍  يتم الآن استخراج البيانات",
        parse_mode="MarkdownV2"
    )
    
    try:
        # Get the largest photo
        photo = message.photo[-1]
        
        # Download the photo
        file = await bot.get_file(photo.file_id)
        file_bytes = await bot.download_file(file.file_path)
        image_data = file_bytes.read()
        
        logger.info(f"Downloaded photo: {len(image_data)} bytes")
        
        # Extract data using OCR
        invoice = await ocr_service.extract_from_image(image_data)
        
        # Check for OCR failure first
        if not invoice.items:
            await processing_msg.edit_text(
                "❌  *حدث خطأ\\!*\n\n"
                "فشل في استخراج البيانات من الصورة",
                parse_mode="MarkdownV2"
            )
            return
        
        # Validate calculations (only if we have items)
        validator.validate(invoice)
        
        # Check for duplicate invoice
        user_id = message.from_user.id
        is_duplicate = db_service.check_duplicate_invoice(
            user_id,
            invoice.invoice_number,
            invoice.tax_number
        )
        
        if is_duplicate:
            # Show duplicate warning
            escaped_num = invoice.invoice_number or "غير محدد"
            for char in ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
                escaped_num = str(escaped_num).replace(char, f'\\{char}')
            
            await processing_msg.edit_text(
                f"⚠️ *هذه الفاتورة مسجلة من قبل\\!*\n\n"
                f"📄 رقم الفاتورة: {escaped_num}\n\n"
                f"هل تريد المتابعة على أي حال؟",
                parse_mode="MarkdownV2",
                reply_markup=get_duplicate_warning_keyboard()
            )
            
            # Store invoice data for later use
            await state.set_state(InvoiceStates.waiting_confirmation)
            await state.update_data(
                invoice_data=invoice,
                message_id=processing_msg.message_id,
                photo_message_id=message.message_id,
                is_duplicate=True
            )
        else:
            # Normal flow - show invoice data
            result_text = format_invoice_result(invoice)
            await processing_msg.edit_text(
                result_text,
                parse_mode="MarkdownV2",
                reply_markup=get_invoice_confirmation_keyboard()
            )
            
            # Store invoice data in state for later use
            await state.set_state(InvoiceStates.waiting_confirmation)
            await state.update_data(
                invoice_data=invoice,
                message_id=processing_msg.message_id,
                photo_message_id=message.message_id
            )
        
    except Exception as e:
        logger.error(f"Error processing photo: {e}")
        # Escape error message for MarkdownV2
        error_msg = str(e)[:100]
        for char in ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']:
            error_msg = error_msg.replace(char, f'\\{char}')
        await processing_msg.edit_text(
            "❌  *حدث خطأ أثناء المعالجة\\!*\n\n"
            f"الخطأ: {error_msg}",
            parse_mode="MarkdownV2"
        )


@router.message(F.document)
async def handle_document(message: Message) -> None:
    """Handle incoming document messages (PDFs)."""
    
    document = message.document
    
    if document.mime_type != "application/pdf":
        await message.answer(
            "⚠️  *نوع الملف غير مدعوم\\!*\n\n"
            "📁  الأنواع المدعومة:\n"
            "    • صور \\(JPG, PNG\\)\n"
            "    • ملفات PDF",
            parse_mode="MarkdownV2"
        )
        return
    
    await message.answer(
        "📄  *تم استلام ملف PDF\\!*\n\n"
        "_دعم PDF قيد التطوير_",
        parse_mode="MarkdownV2"
    )


@router.message()
async def handle_unknown(message: Message) -> None:
    """Handle any other message types."""
    await message.answer(
        "🤔  *لم أفهم هذه الرسالة\\!*\n\n"
        "📌  أنا أتعامل فقط مع:\n\n"
        "    📸  صور الفواتير\n"
        "    📄  ملفات PDF\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "💡  *جرب إرسال صورة فاتورة\\!*",
        parse_mode="MarkdownV2"
    )