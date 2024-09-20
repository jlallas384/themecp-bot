from discord.ext import commands
from config import COMMAND_PREFIX

help_message = f"""
identify <handle> - Set your Codeforces handle
Example:
    {COMMAND_PREFIX}identify noiph

start <level> [tag] - Start a ThemeCP with the given level and tag. If tag is not provided, a random tag will be chosen.
Examples:
    {COMMAND_PREFIX}start 1
    {COMMAND_PREFIX}start 2 math

quit - Quit the ongoing ThemeCP
help - Show this message
"""

class Utils(commands.Cog):
    @commands.command(name='help')
    async def help(self, ctx: commands.Context):
        await ctx.send(f'```{help_message}```')


async def setup(bot):
    await bot.add_cog(Utils())