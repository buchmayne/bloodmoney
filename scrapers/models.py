from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

import settings

DeclarativeBase = declarative_base()


def create_deals_table(engine):
    '''
    ?
    '''
    DeclarativeBase.metadata.create_all(engine)


def db_connect():
    '''
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    '''
    return create_engine(URL(**settings.DATABASE))


class Events(DeclarativeBase):
    """Sqlalchemy event model"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    event_id = Column('event_id', String)
    timestamp = Column('timestamp', DateTime, nullable=True)
    date = Column('date', String, nullable=True)
    gmt = Column('gmt', String, nullable=True)
    venue = Column('venue', String, nullable=True)
    country = Column('country', String, nullable=True)
    city = Column('city', String, nullable=True)
    cur_fight = Column('cur_fight', String, nullable=True)
    event_start = Column('event_start', String, nullable=True)
    event_end = Column('event_end', String, nullable=True)
