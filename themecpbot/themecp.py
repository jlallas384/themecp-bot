import codeforces
from operator import attrgetter
import random
from typing import List
from datetime import datetime

def create_problems(handle: str, level: int):
    def get_problem_ratings():
        with open('data/problem_ratings.txt', 'r') as f:
            return list(map(int, f.readlines()[level - 1].split()))

    def get_solved_problems():
        submissions = codeforces.get_submissions(handle)
        solved_problems = map(attrgetter('problem'), filter(
            lambda sub: sub.verdict == 'OK', submissions))
        return set(solved_problems)

    if level <= 25:
        suggested_tags = ['implementation', 'math', 'brute force',
                          'constructive algorithms', 'greedy', 'sortings']
    elif level <= 40:
        suggested_tags = ['brute force', 'math', 'constructive algorithms', 'graphs',
                          'data structures', 'implementation', 'greedy', 'binary search', 'dp']
    else:
        suggested_tags = ['brute force', 'math', 'constructive algorithms',
                          'graphs', 'bitmasks', 'data structures', 'implementation', 'trees']

    suggested_tag = random.choice(suggested_tags)
    problem_set = codeforces.get_problemset(suggested_tag)
    solved_problems = get_solved_problems()

    unsolved_problems = list(
        filter(lambda problem: problem not in solved_problems, problem_set))

    taken = []
    for rating in get_problem_ratings():
        choices = list(filter(lambda problem: problem.rating ==
                       rating and problem not in taken, unsolved_problems))
        assert choices
        taken.append(random.choice(choices))
    return suggested_tag, taken


def get_level(rating: int):
    rating = max(900, rating)
    with open('data/levels.txt', 'r') as f:
        return max(level for level, bound in enumerate(map(int, f.readlines()), 1) if rating >= bound)

for i in create_problems('jlallas384', 10):
    print(i)
# def get_performance(start_time: datetime, submissions: List[codeforces.Submission]):
#     assert submissions == 4