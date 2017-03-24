from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Record(Base):
    __tablename__ = 'record'
    id = Column(Integer, primary_key=True, autoincrement=True)
    #name = Column