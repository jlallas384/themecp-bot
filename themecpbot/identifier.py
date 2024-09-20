from datetime import datetime, timezone
from typing import List, Tuple

import discord
from discord.ext import tasks, commands

import codeforces
from database import User


def identified_required():
    def predicate(ctx: commands.Context):
        return User.find(ctx.author.id) is not None
    return commands.check(predicate)


class Identifier(commands.Cog):
    def __init__(self):
        self.identify_list: List[Tuple[commands.Context, str]] = []
        self.identify_loop.start()
        self.identify_problem = codeforces.Problem(
            {'contestId': 4, 'index': 'A', 'name': 'Watermelon', 'rating': 800})

    @commands.command(name='identify')
    async def identify(self, ctx: commands.Context, handle: str):
        user = User.find(ctx.author.id)
        if User.find(ctx.author.id) is not None:
            embed = discord.Embed(
                description=f'You are already identified as {user.handle}', color=discord.Color.orange())
            return await ctx.send(embed=embed)

        if any(pending[0].author.id == ctx.author.id for pending in self.identify_list):
            return

        await ctx.send(f'{ctx.author.mention} Please submit a compile error or runtime error in {self.identify_problem.url} within 60 seconds')
        self.identify_list.append((ctx, handle))

    @identify.error
    async def identify_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                description='Please provide your Codeforces handle', color=discord.Color.orange())
            await ctx.send(embed=embed)

    @tasks.loop(seconds=5)
    async def identify_loop(self):
        time = datetime.now(timezone.utc)
        self.identify_list = [(ctx, handle) for ctx, handle in self.identify_list if (
            time - ctx.message.created_at).total_seconds() <= 60]
        new_identify_list = []
        for ctx, handle in self.identify_list:
            try:
                submissions = codeforces.get_submissions(handle, count=1)
            except codeforces.InvalidHandleException:
                submissions = []
            messsage_time = ctx.message.created_at
            identified = False
            if submissions:
                submission = submissions[0]
                if (datetime.fromtimestamp(submission.creation_time_seconds, timezone.utc) >= messsage_time and
                        submission.problem == self.identify_problem and submission.verdict in ('COMPILATION_ERROR', 'RUNTIME_ERROR')):
                    User.create(ctx.author.id, handle)
                    identified = True
                    await ctx.send(f'{ctx.author.mention} has successfully identified as {handle}')
            if not identified:
                new_identify_list.append((ctx, handle))
        self.identify_list = new_identify_list


async def setup(bot):
    await bot.add_cog(Identifier())
