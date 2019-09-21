from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base

import settings

# http://newcoder.io/scrape/part-4/

DeclarativeBase = declarative_base()


def create_eventid_table(engine):
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


class EventId(DeclarativeBase):
    '''
    Table for Fight URL extensions and EventIds
    '''
    __tablename__ = "eventid"

    id = Column(Integer, primary_key=True)
    event_url = Column('event_url', String, nullable=True)
    event_id = Column('event_id', String, nullable=True)


class Events(DeclarativeBase):
    """Events Data Model"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    event_id = Column('event_id', String, nullable=True)
    timestamp = Column('timestamp', DateTime, nullable=True)
    date = Column('date', String, nullable=True)
    gmt = Column('gmt', String, nullable=True)
    venue = Column('venue', String, nullable=True)
    country = Column('country', String, nullable=True)
    city = Column('city', String, nullable=True)
    cur_fight = Column('cur_fight', String, nullable=True)
    event_start = Column('event_start', String, nullable=True)
    event_end = Column('event_end', String, nullable=True)
