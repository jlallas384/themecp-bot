import codeforces
from operator import attrgetter
import random
from typing import List
from config import DATA_FOLDER
from decimal import Decimal, ROUND_HALF_UP

TAGS = ['implementation', 'math', 'brute force', 'constructive algorithms', 'greedy', 'sortings', 'dp', 'graphs', 'data structures',
        'binary search', 'bitmasks', 'trees', 'combinatronics', 'two pointers', 'dsu', 'dfs and similar', 'bitmasks', 'number theory', 'probabilities', 'interactive', 'graphs']


class InvalidTagException(Exception):
    pass


def choose_problems(handle: str, level: int, tag: str = None):
    def get_problem_ratings():
        with open(DATA_FOLDER.joinpath('problem_ratings.txt'), 'r') as f:
            return list(map(int, f.readlines()[level - 1].split()))

    def get_solved_problems():
        submissions = codeforces.get_submissions(handle)
        solved_problems = map(attrgetter('problem'), filter(
            lambda sub: sub.verdict == 'OK', submissions))
        return set(solved_problems)

    def get_random_suggested_tag():
        if level <= 25:
            suggested_tags = ['implementation', 'math', 'brute force',
                              'constructive algorithms', 'greedy', 'sortings']
        elif level <= 40:
            suggested_tags = ['brute force', 'math', 'constructive algorithms', 'graphs',
                              'data structures', 'implementation', 'greedy', 'binary search', 'dp']
        else:
            suggested_tags = ['brute force', 'math', 'constructive algorithms',
                              'graphs', 'bitmasks', 'data structures', 'implementation', 'trees']
        return random.choice(suggested_tags)

    if tag is None:
        tag = get_random_suggested_tag()

    if tag not in TAGS:
        raise InvalidTagException()

    problem_set = codeforces.get_problemset(tag)
    solved_problems = get_solved_problems()

    unsolved_problems = list(
        filter(lambda problem: problem not in solved_problems, problem_set))

    taken: List[codeforces.Problem] = []
    for rating in get_problem_ratings():
        choices = list(filter(lambda problem: problem.rating ==
                       rating and problem not in taken, unsolved_problems))
        assert choices
        taken.append(random.choice(choices))
    return tag, taken

def compute_performance(level: int, ratings: List[int], penalties: List[int]):
    assert len(penalties) == len(ratings) == 4
    num_solved = 0
    while num_solved < 4 and penalties[num_solved] != -1:
        num_solved += 1

    if num_solved == 0:
        ret = ratings[0] - 50
    elif 1 <= num_solved <= 3:
        ret = penalties[num_solved - 1] / 120 * ratings[num_solved - 1] + \
            (120 - penalties[num_solved - 1]) / 120 * ratings[num_solved]
    else:
        ret = penalties[num_solved - 1] / 120 * ratings[num_solved - 1] + \
            (120 - penalties[num_solved - 1]) / 120 * (ratings[3] + 400)

    return Decimal(ret + (level - 1) % 4 * 12.5).to_integral_value(rounding=ROUND_HALF_UP)
