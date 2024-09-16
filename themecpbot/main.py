import asyncio
import discord
from discord.ext import commands
import config



async def main():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents)
    await bot.load_extension('verifier')
    await bot.load_extension('tasker')

    @bot.event
    async def on_ready():
        await bot.change_presence(activity=discord.Game(name=f'{config.COMMAND_PREFIX}help'))

    if config.TOKEN is None:
        raise Exception('TOKEN is not found')

    await bot.start(config.TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
