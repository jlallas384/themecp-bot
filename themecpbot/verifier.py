import codeforces
from discord.ext import tasks, commands
from datetime import datetime, timezone
from typing import List, Tuple


class Verifier(commands.Cog):
    def __init__(self):
        self.verify_list: List[Tuple[commands.Context, str]] = []
        self.verify_loop.start()
        self.verify_problem = codeforces.Problem(
            {'contestId': 4, 'index': 'A', 'name': 'Watermelon', 'rating': 800})

    @commands.command(name='verify')
    async def verify_command(self, ctx: commands.context, handle: str):
        await ctx.send(f'{ctx.author.mention} Please submit a compile error in {self.verify_problem.url} within 60 seconds')
        self.verify_list.append((ctx, handle))

    @tasks.loop(seconds=5)
    async def verify_loop(self):
        time = datetime.now(timezone.utc)
        self.verify_list = [(ctx, handle) for ctx, handle in self.verify_list if (
            time - ctx.message.created_at).total_seconds() <= 60]
        new_verify_list = []
        for ctx, handle in self.verify_list:
            submissions = codeforces.get_submissions(handle, count=1)
            messsage_time = ctx.message.created_at
            verified = False
            if submissions:
                submission = submissions[0]
                if (datetime.fromtimestamp(submission.creation_time_seconds, timezone.utc) >= messsage_time and
                        submission.problem == self.verify_problem and submission.verdict == 'COMPILATION_ERROR'):
                    await ctx.send(f'{ctx.author.mention} has successfully verified')
                    verified = True
            if not verified:
                new_verify_list.append((ctx, handle))
        self.verify_list = new_verify_list
