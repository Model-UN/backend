from bot.logger import logger as bot_logger
from bot import bot
from settings import settings


if __name__ == "__main__":
    bot_logger.info("Starting bot...")
    bot.run(settings.token)
