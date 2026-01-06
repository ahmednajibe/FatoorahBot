"""
FatoorahBot - Handlers Package
"""
from bot.handlers.start import router as start_router
from bot.handlers.invoice import router as invoice_router
from bot.handlers.callbacks import router as callbacks_router
from bot.handlers.edit_handlers import router as edit_router
from bot.handlers.item_edit_handlers import router as item_edit_router
from bot.handlers.export import router as export_router
from bot.handlers.menu_handlers import router as menu_router

# List of all routers to include
all_routers = [
    start_router,
    menu_router,  # Menu handlers
    export_router,  # Export commands
    callbacks_router,  # Invoice callbacks
    item_edit_router,  # Item edit handlers
    edit_router,  # Edit handlers
    invoice_router,  # Invoice handler last (catches photos)
]