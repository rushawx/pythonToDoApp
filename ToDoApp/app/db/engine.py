import datetime
import os

import sqlalchemy as sa
from dotenv import load_dotenv
from sqlalchemy import Boolean, Column, DateTime, String, UUID
from sqlalchemy.orm import sessionmaker


load_dotenv()

DB_URL = os.getenv("DB_URL")

engine = sa.create_engine(DB_URL)

session = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = sa.orm.declarative_base()


class Item(Base):
    __tablename__ = "items"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    todo = Column(DateTime)
    done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(
        DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now
    )
