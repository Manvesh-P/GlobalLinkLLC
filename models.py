from sqlalchemy import (Column, 
                        Integer, 
                        String, 
                        )
from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base


_schema = 'dev_globallink_llc'
Base = declarative_base(metadata=MetaData(schema=_schema))
# Base = declarative_base()

class User(Base):
    __tablename__ = 'users_data'
    __table_args__ = {'schema': 'dev_globallink_llc'}

    _id = Column(Integer, primary_key=True, autoincrement=True)
    # first_name = Column(String)
    # last_name = Column(String)
    username = Column(String, unique=True)
    password = Column(String)
    email = Column(String, unique=True)
    # mobile_number = Column(String, unique=True)
