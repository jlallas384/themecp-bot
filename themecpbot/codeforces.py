import requests
from dataclasses import dataclass

CODEFORCES_URL = 'https://codeforces.com'


class InvalidHandleException(Exception):
    pass


@dataclass(init=False, unsafe_hash=True)
class Problem:
    contest_id: int | None
    index: str
    name: str
    rating: int | None
    def __init__(self, value):
        self.contest_id = value.get('contestId', None)
        self.index = value['index']
        self.name = value['name']
        self.rating = value.get('rating', None)

    @property
    def url(self):
        return f'{CODEFORCES_URL}/contest/{self.contest_id}/problem/{self.index}'


@dataclass(init=False)
class Submission:
    problem: Problem
    verdict: str | None
    creation_time_seconds: int

    def __init__(self, value):
        self.problem = Problem(value['problem'])
        self.verdict = value.get('verdict', None)
        self.creation_time_seconds = value['creationTimeSeconds']


def get_problemset(*args):
    resp = requests.get(f'{CODEFORCES_URL}/api/problemset.problems',
                        params={'tags': ';'.join(args)})
    if resp.status_code != 200:
        raise Exception('Failed to fetch problemset')
    data = resp.json()
    assert data['status'] == 'OK'
    return list(map(Problem, data['result']['problems']))


def get_submissions(handle: str, count=None):
    resp = requests.get(f'{CODEFORCES_URL}/api/user.status',
                        params={'handle': handle, 'count': count})
    if resp.status_code != 200:
        raise Exception('Failed to fetch submissions')
    data = resp.json()
    if data['status'] != 'OK':
        raise InvalidHandleException()
    return list(map(Submission, data['result']))


def get_rating(handle: str):
    resp = requests.get(f'{CODEFORCES_URL}/api/user.rating',
                        params={'handle': handle})
    if resp.status_code != 200:
        raise Exception('Failed to fetch rating')
    data = resp.json()
    if data['status'] != 'OK':
        raise InvalidHandleException()
    ratings = data['result']
    return ratings[-1]['newRating'] if ratings else 0
