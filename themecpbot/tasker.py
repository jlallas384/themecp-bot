from verifier import verified_required
from discord.ext import commands
import discord
import themecp
from database import User

# @start.error
# async def start_error(ctx: commands.Context, error: commands.CommandError):
#     if isinstance(error, commands.CheckFailure):
#         await ctx.send(f'You are not verified yet. Please verify first using the `$themecp verify` command')


class Tasker(commands.Cog):
    @commands.command(name='start')
    async def start(self, ctx: commands.Context):
        user = User.find(ctx.author.id)
        tag, problems = themecp.choose_problems(user.handle, user.level)
        embeds = [discord.Embed(title=problem.name, url=problem.url,
                                description=f'Rating: {problem.rating}') for problem in problems]
        await ctx.send(f'Tag: {tag}', embeds=embeds)
        await ctx.send(f'Good luck! {ctx.author.mention}')


async def setup(bot):
    await bot.add_cog(Tasker())
