from datetime import datetime, timezone, timedelta
from typing import List
import logging

from discord.ext import commands, tasks
import discord
from table2ascii import table2ascii, Alignment

from identifier import identified_required
import themecp
import database as db
import codeforces
from config import COMMAND_PREFIX

CONTEST_LENGTH = timedelta(hours=2)


async def handle_ongoing(user: db.User, ctx: commands.Context):
    time_left = user.current_contest.date_started.replace(
        tzinfo=timezone.utc) + CONTEST_LENGTH - datetime.now(tz=timezone.utc)
    minutes = (time_left.seconds + 59) // 60
    minutes_str = f'{minutes} minute' if minutes == 1 else f'{minutes} minutes'
    embed = discord.Embed(
        description=f'You still have an ongoing ThemeCP which ends in {minutes_str}. Please finish it first or quit using the `{COMMAND_PREFIX}quit` command.',
        color=discord.Color.orange()
    )
    return await ctx.send(embed=embed)


def is_problem_solved(submissions: List[codeforces.Submission], problem_info: db.ProblemInfo):
    for submission in submissions:
        problem = submission.problem
        if submission.verdict == 'OK' and (problem.contest_id, problem.index) == (problem_info.contest_id, problem_info.index):
            return datetime.fromtimestamp(submission.creation_time_seconds, timezone.utc)


def build_results(contest: db.VirtualContest):
    penalties = [
        -1 if problem.date_solved is None
        else int(
            (problem.date_solved.replace(tzinfo=timezone.utc) -
             contest.date_started.replace(tzinfo=timezone.utc)).total_seconds() / 60
        )
        for problem in contest.problems
    ]
    table = table2ascii(
        header=['#', 'Name', 'Rating', 'Penalty'],
        body=[
            [num, problem.problem_info.name, problem.problem_info.rating,
                penalty if penalty != -1 else 'N/A']
            for num, (problem, penalty) in enumerate(zip(contest.problems, penalties), 1)
        ],
        alignments=[Alignment.LEFT, Alignment.LEFT,
                    Alignment.LEFT, Alignment.LEFT]
    )
    performance = themecp.compute_performance(
        contest.level, [problem.problem_info.rating for problem in contest.problems], penalties)
    return f'```{table}\nPerformance: {performance}\n```'


class Tasker(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.solved_checker_loop.start()

    @commands.command(name='start')
    @identified_required()
    async def start(self, ctx: commands.Context, level: int, *, tag: str = None):
        user = db.User.find(ctx.author.id)
        logging.info('start %s %d %s', user.handle, level, tag)

        if user.current_contest is not None:
            return await handle_ongoing(user, ctx)

        if not (1 <= level <= 109):
            embed = discord.Embed(
                description='Level must be between 1 and 109', color=discord.Color.orange())
            return await ctx.send(embed=embed)

        try:
            tag, problems = themecp.choose_problems(user.handle, level, tag)
        except themecp.InvalidTagException:
            embed = discord.Embed(
                description=f'{tag} is not a valid tag', color=discord.Color.orange())
            return await ctx.send(embed=embed)

        if len(problems) < 4:
            embed = discord.Embed(
                description='Not enough problems', color=discord.Color.orange())
            return await ctx.send(embed=embed)

        contest = user.create_contest(tag, ctx.channel.id, level)
        for problem in problems:
            contest.add_problem(problem.contest_id,
                                problem.index, problem.name, problem.rating)

        embeds = [discord.Embed(title=problem.name, url=problem.url,
                                description=f'Rating: {problem.rating}') for problem in problems]
        await ctx.reply(f'Tag: {tag}', embeds=embeds)
        await ctx.send(f'Good luck! {ctx.author.mention}')

    @start.error
    async def start_error(self, ctx: commands.Context, error: commands.CommandError):
        if isinstance(error, commands.CheckFailure):
            embed = discord.Embed(
                description=f'You are not identified yet. Please identify first using the `{COMMAND_PREFIX}identify` command', color=discord.Color.orange())
            await ctx.send(embed=embed)
        if isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(
                description='Please provide your level', color=discord.Color.orange())
            await ctx.send(embed=embed)
            
    @tasks.loop(seconds=45)
    async def solved_checker_loop(self):
        for contest in db.VirtualContest.get_active():
            date_started = contest.date_started.replace(tzinfo=timezone.utc)
            user = contest.user
            unsolved_problems = contest.get_unsolved_problems()
            submissions = list(
                reversed(codeforces.get_submissions(user.handle, count=10)))

            for unsolved in unsolved_problems:
                date_solved = is_problem_solved(
                    submissions, unsolved.problem_info)
                if date_solved is not None and date_solved < date_started + CONTEST_LENGTH:
                    unsolved.set_date_solved(date_solved)

            has_solved_all = all(
                problem.date_solved is not None for problem in contest.problems)
            if has_solved_all:
                await self.contest_success(user.user_id, contest.channel_id)
            elif date_started + CONTEST_LENGTH <= datetime.now(timezone.utc):
                await self.contest_fail(user.user_id, contest.channel_id)

    async def get_user_and_channel(self, user_id: int, channel_id: int):
        user = await self.bot.fetch_user(user_id)
        channel = await self.bot.fetch_channel(channel_id)
        return user, channel

    async def contest_success(self, user_id: int, channel_id: int):
        user, channel = await self.get_user_and_channel(user_id, channel_id)
        contest = db.User.find(user_id).current_contest

        results = build_results(contest)
        await channel.send(f"Yay! {user.mention}\n{results}")
        contest.finish()

    async def contest_fail(self, user_id: int, channel_id: int):
        user, channel = await self.get_user_and_channel(user_id, channel_id)
        contest = db.User.find(user_id).current_contest

        results = build_results(contest)
        await channel.send(f"Time's up! {user.mention}\n{results}")
        contest.finish()

    @commands.command(name='quit')
    async def quit(self, ctx: commands.Context):
        embed = discord.Embed(
            description='No quitting', color=discord.Color.orange())
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Tasker(bot))
