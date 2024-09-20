import asyncio
import discord
from discord.ext import commands
import config



async def main():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents, help_command=None)

    await bot.load_extension('identifier')
    await bot.load_extension('tasker')
    await bot.load_extension('utils')

    @bot.event
    async def on_ready():
        await bot.change_presence(activity=discord.Game(name=f'{config.COMMAND_PREFIX}help'))

    if config.TOKEN is None:
        raise ValueError('TOKEN is not found')

    discord.utils.setup_logging()
    await bot.start(config.TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
