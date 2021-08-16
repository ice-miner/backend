from sqlalchemy import Column, Integer, String, create_engine, event, Float
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.schema import ForeignKey, MetaData
from contextlib import contextmanager
from sqlalchemy.sql.sqltypes import DateTime

from dotenv import load_dotenv
import os

from sqlalchemy.sql.sqltypes import TIMESTAMP
load_dotenv()

postgres_pw = os.environ["POSTGRES_ICEDATA_PASSWORD"]
Base = declarative_base()
engine = create_engine(f'postgresql+psycopg2://icedata:{postgres_pw}@localhost/icedata', echo=True)

Session = sessionmaker()
Session.configure(bind=engine)

Base = declarative_base(bind=engine)
meta: MetaData = Base.metadata

class Train(Base):
    __tablename__ = 'trains'

    id = Column(Integer, primary_key=True)
    trainType = Column(String)
    tzn = Column(String, unique=True)
    series = Column(Integer)


class TPoint(Base):
    __tablename__ = 'tpoints'
    timestamp = Column(DateTime, primary_key=True)
    connection = Column(String)
    serviceLevel = Column(String)
    gpsStatus = Column(String)
    internet = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    speed = Column(Float)
    train_id = Column(Integer, ForeignKey('trains.id'), primary_key=True)
    train = relationship("Train", backref="points")

    def to_dict(self):
        return {
            "timestamp": self.timestamp,
            "speed":self.speed,
            "longitude": self.longitude,
            "latitude":self.latitude
        }

@event.listens_for(TPoint.__table__, 'after_create')
def make_hypertable(target, connection, **_):
    tablename = target.name
    columname = target.primary_key.columns[0].name
    connection.execute(
        f"SELECT create_hypertable('{tablename}', '{columname}');"
    )

@event.listens_for(engine, 'first_connect')
def receive_first_connect(connection, _):
    with connection.cursor() as c:
        c.execute(
            "CREATE EXTENSION IF NOT EXISTS timescaledb;"
        )

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    with session_scope() as session:
        meta.drop_all()
        meta.create_all(engine)
