
from datetime import datetime
from sqlalchemy import Float, Table, Column, Integer, String, DateTime
from database import base


class User(base):
    __tablename__ = "user_data"
    id = Column(Integer,primary_key=True,index=True,autoincrement=True)
    username = Column(String,nullable=False)
    password = Column(String,nullable=False)
    role = Column(String,nullable=False)


class Bin(base):
    __tablename__ = 'bins'
    bin_id = Column(Integer, primary_key=True)
    distance = Column(Float)
    temperature = Column(Float)
    lat = Column(Float)
    lon = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)


class BinHistory(base):
    __tablename__ = 'bin_history'
    id = Column(Integer, primary_key=True)
    bin_id = Column(String)
    distance = Column(Float)
    temperature = Column(Float)
    lat = Column(Float)
    lon = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
