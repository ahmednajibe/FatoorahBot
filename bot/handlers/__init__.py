"""
FatoorahBot - Handlers Package
"""
from bot.handlers.start import router as start_router
from bot.handlers.invoice import router as invoice_router

# List of all routers to include
all_routers = [
    start_router,
    invoice_router,
]