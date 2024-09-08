import discord
from discord.ext.commands import Bot
from verifier import Verifier


intents = discord.Intents.default()
intents.message_content = True

bot = Bot(command_prefix='$themecp ', intents=intents)


@bot.event
async def on_ready():
    await bot.add_cog(Verifier())
    print('Bot is ready')

bot.run('MTI4MjIyNDU2ODk0NTM0NDYyMg.GYv2Gn.1hZz3mipVIEm4w7oBd7735KgKTX3hyOY4fp26g')
