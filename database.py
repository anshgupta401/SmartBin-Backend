from sqlalchemy import create_engine, MetaData
from databases import Database

from sqlalchemy.orm import sessionmaker,declarative_base

import os
from dotenv import load_dotenv

load_dotenv()
database_one = Database(os.getenv("DATABASE_URL"))

engine = create_engine(os.getenv("DATABASE_URL"))

local_session = sessionmaker(bind=engine,autoflush=False,autocommit=False)

metaData = MetaData()

base = declarative_base()