"""
Inline Keyboards
Interactive buttons for invoice confirmation and editing
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_invoice_confirmation_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for initial invoice confirmation."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ حفظ الفاتورة", callback_data="invoice_save"),
            InlineKeyboardButton(text="✏️ تعديل", callback_data="invoice_edit")
        ],
        [
            InlineKeyboardButton(text="❌ إلغاء", callback_data="invoice_cancel")
        ]
    ])


def get_edit_menu_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for edit menu."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 تعديل المورد", callback_data="edit_supplier"),
            InlineKeyboardButton(text="📝 تعديل التاريخ", callback_data="edit_date")
        ],
        [
            InlineKeyboardButton(text="📝 تعديل رقم الفاتورة", callback_data="edit_invoice_num"),
            InlineKeyboardButton(text="📝 تعديل الرقم الضريبي", callback_data="edit_tax_num")
        ],
        [
            InlineKeyboardButton(text="📝 تعديل الأصناف", callback_data="edit_items")
        ],
        [
            InlineKeyboardButton(text="📝 تعديل الإجماليات", callback_data="edit_totals")
        ],
        [
            InlineKeyboardButton(text="✅ حفظ التعديلات", callback_data="invoice_save"),
            InlineKeyboardButton(text="🔙 رجوع", callback_data="invoice_cancel")
        ]
    ])


def get_totals_edit_keyboard() -> InlineKeyboardMarkup:
    """Keyboard for editing totals."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 الخصم", callback_data="edit_discount"),
            InlineKeyboardButton(text="📝 نسبة الضريبة", callback_data="edit_tax_rate")
        ],
        [
            InlineKeyboardButton(text="🔙 رجوع", callback_data="invoice_edit")
        ]
    ])


def get_items_list_keyboard(items_count: int) -> InlineKeyboardMarkup:
    """Keyboard for selecting which item to edit."""
    buttons = []
    
    # Add button for each item
    for i in range(items_count):
        buttons.append([InlineKeyboardButton(
            text=f"📦 صنف {i+1}",
            callback_data=f"select_item_{i}"
        )])
    
    # Add back button
    buttons.append([InlineKeyboardButton(text="🔙 رجوع", callback_data="invoice_edit")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_item_edit_keyboard(item_index: int) -> InlineKeyboardMarkup:
    """Keyboard for editing a specific item."""
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="📝 اسم الصنف", callback_data=f"edit_item_name_{item_index}"),
            InlineKeyboardButton(text="📝 الكمية", callback_data=f"edit_item_qty_{item_index}")
        ],
        [
            InlineKeyboardButton(text="📝 الوحدة", callback_data=f"edit_item_unit_{item_index}"),
            InlineKeyboardButton(text="📝 سعر الوحدة", callback_data=f"edit_item_price_{item_index}")
        ],
        [
            InlineKeyboardButton(text="❌ حذف الصنف", callback_data=f"delete_item_{item_index}"),
            InlineKeyboardButton(text="🔙 رجوع", callback_data="edit_items")
        ]
    ])
