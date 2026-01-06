"""
Start Command Handler
Handles /start and /help commands with interactive menu
"""
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu keyboard."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 تقارير الفواتير", callback_data="menu_invoices"),
            InlineKeyboardButton(text="📦 تقارير الأصناف", callback_data="menu_items")
        ],
        [
            InlineKeyboardButton(text="📈 إحصائياتي", callback_data="menu_stats"),
            InlineKeyboardButton(text="❓ المساعدة", callback_data="menu_help")
        ]
    ])


def get_invoices_menu_keyboard() -> InlineKeyboardMarkup:
    """Invoices export menu."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📊 كل الفواتير", callback_data="export_all_invoices")
        ],
        [
            InlineKeyboardButton(text="📅 فواتير بتاريخ محدد", callback_data="export_invoices_date")
        ],
        [
            InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="menu_main")
        ]
    ])


def get_items_menu_keyboard() -> InlineKeyboardMarkup:
    """Items export menu."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📦 كل الأصناف", callback_data="export_all_items")
        ],
        [
            InlineKeyboardButton(text="📅 أصناف بتاريخ محدد", callback_data="export_items_date")
        ],
        [
            InlineKeyboardButton(text="🔙 القائمة الرئيسية", callback_data="menu_main")
        ]
    ])


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    """Handle /start command."""
    welcome_text = (
        "🧾 مرحباً بك في FatoorahBot!\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "أنا بوت ذكي لاستخراج بيانات الفواتير.\n\n"
        "📌 كيف تستخدمني؟\n\n"
        "    1️⃣ أرسل صورة فاتورة\n"
        "    2️⃣ سأقوم بتحليلها واستخراج البيانات\n"
        "    3️⃣ راجع البيانات وعدّلها إن لزم\n"
        "    4️⃣ احفظ الفاتورة في قاعدة البيانات\n"
        "    5️⃣ صدّر تقارير Excel متى أردت\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📸 ابدأ الآن بإرسال صورة فاتورة!\n\n"
        "أو اختر من القائمة:"
    )
    await message.answer(welcome_text, reply_markup=get_main_menu_keyboard())


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Handle /help command."""
    help_text = (
        "📖 المساعدة\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📁 أنواع الملفات المدعومة:\n"
        "    • صور (JPG, PNG)\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📋 الأوامر المتاحة:\n\n"
        "    /start - بدء المحادثة\n"
        "    /help - المساعدة\n"
        "    /stats - الإحصائيات\n"
        "    /export_invoices - تصدير كل الفواتير\n"
        "    /export_items - تصدير كل الأصناف\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "📊 البيانات المستخرجة:\n"
        "    • اسم المورد\n"
        "    • الرقم الضريبي\n"
        "    • تاريخ الفاتورة\n"
        "    • رقم الفاتورة\n"
        "    • جدول الأصناف\n"
        "    • الإجمالي شامل الضريبة\n\n"
        "━━━━━━━━━━━━━━━━━━━━\n\n"
        "💬 للدعم: تواصل مع المطور"
    )
    await message.answer(help_text, reply_markup=get_main_menu_keyboard())