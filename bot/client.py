import discord

from bot.logger import logger


class Client(discord.Client):
    async def on_ready(self):
        logger.info(f'Logged in as {self.user}')

    async def on_message(self, message):
        if message.author == self.user:
            return

        if message.content == 'ping':
            await message.channel.send('pong')
