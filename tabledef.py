from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
 
engine = create_engine('sqlite:///tutorial.db', echo=True)
Base = declarative_base()
 
########################################################################
class Cluster(Base):
    """"""
    __tablename__ = "cluster"
 
    id = Column(Integer, primary_key=True)
    instance = Column(String)
    floating_ip = Column(String)
    floating_ip_id = Column(String)
 
    #----------------------------------------------------------------------
    def __init__(self, instance, floating_ip, floating_ip_id):
        """"""
        self.instance = instance
        self.floating_ip = floating_ip
        self.floating_ip_id = floating_ip_id

class User(Base):
    """"""
    __tablename__ = "users"
 
    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
 
    #----------------------------------------------------------------------
    def __init__(self, username, password):
        """"""
        self.username = username
        self.password = password

# create tables
Base.metadata.create_all(engine)