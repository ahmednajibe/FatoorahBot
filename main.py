"""
FatoorahBot - Main Entry Point
Telegram bot for extracting invoice data using AI
"""
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from config.settings import settings
from bot.handlers import all_routers


# Configure logging
logging.basicConfig(
    level=logging.DEBUG if settings.DEBUG else logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Main function to start the bot."""
    
    # Validate settings before starting
    settings.validate()
    
    # Initialize bot with token
    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    
    # Initialize dispatcher
    dp = Dispatcher()
    
    # Register all routers
    for router in all_routers:
        dp.include_router(router)
    
    # Log startup
    logger.info("🚀 FatoorahBot is starting...")
    logger.info(f"📋 Registered {len(all_routers)} routers")
    
    # Start polling
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())