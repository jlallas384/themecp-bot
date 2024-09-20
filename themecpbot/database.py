from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy import create_engine, String, ForeignKey, BigInteger
from sqlalchemy.orm import sessionmaker, relationship, Mapped, mapped_column, DeclarativeBase

from config import DATABASE_URL


engine = create_engine(DATABASE_URL)

Session = sessionmaker(bind=engine)
session = Session()


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    handle: Mapped[str] = mapped_column(String(24))
    contests: Mapped[List['VirtualContest']
                     ] = relationship(back_populates='user')

    @staticmethod
    def create(user_id: int, handle: str):
        session.add(User(user_id=user_id, handle=handle))
        session.commit()

    @staticmethod
    def find(user_id: int):
        return session.get(User, user_id)

    def create_contest(self, tag: str, channel_id: int, level: int):
        contest = VirtualContest(user=self, tag=tag, channel_id=channel_id, level=level)
        session.add(contest)
        session.commit()
        return contest

    @property
    def current_contest(self):
        contest = next((c for c in self.contests if not c.finished), None)
        return contest


class ProblemInfo(Base):
    __tablename__ = 'problem_infos'
    problem_info_id: Mapped[int] = mapped_column(primary_key=True)
    contest_id: Mapped[int]
    index: Mapped[str] = mapped_column(String(3))
    name: Mapped[str]
    rating: Mapped[int]

    @staticmethod
    def create(contest_id: int, index: str, name: str, rating: int):
        problem_info = session.query(ProblemInfo).where(
            (ProblemInfo.contest_id == contest_id) & (ProblemInfo.index == index)).first()
        if problem_info is None:
            problem_info = ProblemInfo(contest_id=contest_id, index=index, name=name, rating=rating)
            session.add(problem_info)
            session.commit()
        return problem_info


class VirtualContest(Base):
    __tablename__ = 'virtual_contests'

    virtual_contest_id: Mapped[int] = mapped_column(primary_key=True)
    date_started: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc))
    finished: Mapped[bool] = mapped_column(default=False)
    tag: Mapped[str]
    level: Mapped[int]
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.user_id'))
    channel_id: Mapped[int] = mapped_column(BigInteger)
    problems: Mapped[List['Problem']] = relationship(
        order_by='Problem.problem_id')
    user: Mapped[User] = relationship(back_populates='contests')

    def add_problem(self, contest_id: int, index: str, title: str, rating: int):
        problem_info = ProblemInfo.create(contest_id, index, title, rating)
        problem = Problem(problem_info=problem_info,
                          virtual_contest_id=self.virtual_contest_id)
        session.add(problem)
        session.commit()

    def get_unsolved_problems(self):
        return [problem for problem in self.problems if problem.date_solved is None]

    @staticmethod
    def get_active():
        return session.query(VirtualContest).where(VirtualContest.finished == False).all()

    def finish(self):
        self.finished = True
        session.commit()


class Problem(Base):
    __tablename__ = 'problems'

    problem_id: Mapped[int] = mapped_column(
        primary_key=True, autoincrement=True)
    date_solved: Mapped[Optional[datetime]]

    problem_info_id: Mapped[int] = mapped_column(
        ForeignKey('problem_infos.problem_info_id'))
    virtual_contest_id: Mapped[int] = mapped_column(
        ForeignKey('virtual_contests.virtual_contest_id'))

    problem_info: Mapped[ProblemInfo] = relationship()

    def set_date_solved(self, date_solved):
        self.date_solved = date_solved
        session.commit()


Base.metadata.create_all(engine)
