"""
Main entry point for the Telegram bot.
"""

import asyncio
import logging
from .bot import dp, bot as telegram_bot

# Configure logging (only if not already configured by bot.py)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Start the bot."""
    logger.info("Starting Telegram bot...")
    # Delete webhook to avoid conflict with getUpdates
    await telegram_bot.delete_webhook()
    try:
        await dp.start_polling(telegram_bot)
    except Exception as e:
        logger.error(f"Error starting bot: {str(e)}")
        raise
    finally:
        await telegram_bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())