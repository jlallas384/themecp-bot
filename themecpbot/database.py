from sqlalchemy import create_engine, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship, Mapped, mapped_column
from config import DATABASE_URL
from datetime import datetime, timezone
from typing import List, Optional

engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True)
    handle: Mapped[str] = mapped_column(String(24))
    level: Mapped[int]
    virtual_contests: Mapped[List['VirtualContest']] = relationship(
        'VirtualContest', back_populates='user')

    @staticmethod
    def create(user_id: int, handle: str, level: int):
        session.add(User(user_id=user_id, handle=handle, level=level))
        session.commit()

    @staticmethod
    def find(user_id: int):
        return session.get(User, user_id)

    def create_contest(self):
        contest = VirtualContest(self)
        session.add(contest)
        session.commit()
        return contest

    @property
    def current_contest(self):
        contest = next((c for c in self.contests if not c.finished), None)
        return contest


class ProblemInfo(Base):
    __tablename__ = 'problem_info'
    problem_info_id: Mapped[int] = mapped_column(primary_key=True)
    contest_id: Mapped[int]
    index: Mapped[str] = mapped_column(String(3))

    @staticmethod
    def create(contest_id: int, index: str):
        problem_info = session.query(ProblemInfo).where(
            ProblemInfo.contest_id == contest_id and ProblemInfo.index == index).first()
        if problem_info is None:
            problem_info = ProblemInfo(contest_id=contest_id, index=index)
            session.add(problem_info)
            session.commit()
        return problem_info


class VirtualContest(Base):
    __tablename__ = 'virtual_contests'

    virtual_contest_id: Mapped[int] = mapped_column(primary_key=True)
    date_started: Mapped[datetime]
    finished: Mapped[bool]

    user_id: Mapped[int] = mapped_column(ForeignKey('users.user_id'))

    problems: Mapped[List['Problem']] = relationship('Problem')
    user: Mapped[User] = relationship('User', back_populates='contests')

    @staticmethod
    def __init__(self, user: User):
        self.user_id = user.user_id
        self.date_started = datetime.now(timezone.utc)
        self.finished = False

    def add_problem(self, contest_id: int, index: str):
        problem_info = ProblemInfo.create(contest_id, index)
        problem = Problem(
            problem_info_id=problem_info.problem_info_id, contest_id=self.virtual_contest_id)
        session.add(problem)
        session.commit()

    def get_unsolved_problems(self):
        return [problem for problem in self.problems if problem.date_solved is None]

    @staticmethod
    def get_active():
        return session.query(VirtualContest).where(VirtualContest.finished == False).all()


class Problem(Base):
    __tablename__ = 'problems'

    problem_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True)
    date_solved: Mapped[Optional[int]]

    problem_info_id: Mapped[int] = mapped_column(
        ForeignKey('problem_info.problem_info_id'))
    contest_id: Mapped[int] = mapped_column(ForeignKey('contests.contest_id'))

    problem_info: Mapped[ProblemInfo] = relationship('ProblemInfo')


Base.metadata.create_all(engine)
