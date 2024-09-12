import discord
from discord.ext import commands
import config
import asyncio
from database import User

async def main():
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix=config.COMMAND_PREFIX, intents=intents)
    
    await bot.load_extension('verifier')
    await bot.load_extension('tasker')

    if config.TOKEN is None:
        print('TOKEN is not found')
        exit(1)

    await bot.start(config.TOKEN)

if __name__ == '__main__':
    asyncio.run(main())
