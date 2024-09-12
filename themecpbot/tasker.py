from verifier import verified_required
from discord.ext import commands, tasks
import discord
import themecp
import database as db
from datetime import datetime, timezone, timedelta
import codeforces
from typing import List
from config import COMMAND_PREFIX

class Tasker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.solved_checker_loop.start()

    @commands.command(name='start')
    @verified_required()
    async def start(self, ctx: commands.Context):
        user = db.User.find(ctx.author.id)
        if user.current_contest is not None:
            return await ctx.send('You are still in a contest. Please finish it first.')

        tag, problems = themecp.choose_problems(user.handle, user.level)
        contest = user.create_contest(tag, ctx.channel.id)
        for problem in problems:
            contest.add_problem(problem.contest_id, problem.index)

        embeds = [discord.Embed(title=problem.name, url=problem.url,
                                description=f'Rating: {problem.rating}') for problem in problems]
        await ctx.send(f'Tag: {tag}', embeds=embeds)
        await ctx.send(f'Good luck! {ctx.author.mention}')

    @start.error
    async def start_error(ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            await ctx.send(f'You are not verified yet. Please verify first using the `{COMMAND_PREFIX}verify` command')

    def is_problem_solved(self, submissions: List[codeforces.Submission], problem_info: db.ProblemInfo):
        for submission in submissions:
            problem = submission.problem
            if submission.verdict == 'OK' and (problem.contest_id, problem.index) == (problem_info.contest_id, problem_info.index):
                return datetime.fromtimestamp(submission.creation_time_seconds, timezone.utc)

    @tasks.loop(seconds=5)
    async def solved_checker_loop(self):
        for contest in db.VirtualContest.get_active():
            date_started = contest.date_started.replace(tzinfo=timezone.utc)
            user = contest.user
            unsolved_problems = contest.get_unsolved_problems()
            submissions = list(
                reversed(codeforces.get_submissions(user.handle, count=10)))
            for unsolved in unsolved_problems:
                date_solved = self.is_problem_solved(
                    submissions, unsolved.problem_info)
                if date_solved is not None and date_solved < date_started + timedelta(hours=2):
                    unsolved.set_date_solved(date_solved)

            has_solved_all = all(
                problem.date_solved is not None for problem in contest.problems)
            if has_solved_all:
                contest.finish()
                await self.congratulate_user(user.user_id, contest.channel_id)
            elif date_started + timedelta(hours=2) <= datetime.now(timezone.utc):
                contest.finish()

    async def get_user_and_channel(self, user_id: int, channel_id: int):
        user = await self.bot.fetch_user(user_id)
        channel = await self.bot.fetch_channel(channel_id)
        return user, channel

    async def congratulate_user(self, user_id: int, channel_id: int):
        user, channel = self.get_user_and_channel(user_id, channel_id)
        await channel.send(f'{user.mention} yay +1')


async def setup(bot):
    await bot.add_cog(Tasker(bot))
