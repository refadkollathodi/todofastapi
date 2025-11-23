from sqlalchemy import Column,String,Boolean,Integer
from database import Base

class TodoItem(Base):
    __tablename__='todo_items'
    id=Column(Integer,primary_key=True,index=True)
    user=Column(String(50),index=True)
    task=Column(String(50),index=True)
class User(Base):
    __tablename__='users'
    id=Column(Integer,primary_key=True,index=True)
    username=Column(String(50),unique=True,index=True)
    hashed_password=Column(String(100))
    disabled=Column(Boolean,default=False)


