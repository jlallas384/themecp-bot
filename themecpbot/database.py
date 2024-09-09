from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=True)

Session = sessionmaker(bind=engine)
session = Session()

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    uid = Column('uid', Integer, primary_key=True)
    handle = Column('handle', String(24))
    level = Column('level', Integer)

    def __init__(self, uid: int, handle: str, level: int):
        self.uid = uid
        self.handle = handle
        self.level = level

    @staticmethod
    def create(uid: int, handle: str, level: int):
        session.add(User(uid, handle, level))
        session.commit()

    @staticmethod
    def find(uid: int):
        return session.query(User).where(User.uid == uid).first()


Base.metadata.create_all(engine)
