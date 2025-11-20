from typing import Union
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel

import models
from database import engine,SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends,status


app = FastAPI()
models.Base.metadata.create_all(bind=engine)


class Todolist(BaseModel):
    task: str
    user:str

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()



@app.get("/list/{user}")
def get_items_user(user:str,db:Session=Depends(get_db)):
   result = db.query(models.TodoItem).filter(models.TodoItem.user==user).all()
   if not result:
    raise HTTPException(status_code=404, detail="item not found")
   return result
    


@app.get("/list")
def get_items(db:Session=Depends(get_db)):
    item=db.query(models.TodoItem).all()
    return item

@app.post("/list",status_code=status.HTTP_201_CREATED)
def add_item(item:Todolist,db:Session=Depends(get_db)):
    new_item=models.TodoItem(
        user=item.user,
        task=item.task
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item

@app.put("/list",status_code=status.HTTP_201_CREATED)
def update_item(item:Todolist,db:Session=Depends(get_db)):
    todo_item=db.query(models.TodoItem).filter(models.TodoItem.id==item.id).first()
    if not todo_item:
     raise HTTPException(status_code=404, detail="item not found")
    todo_item.user=item.user
    todo_item.task=item.task
    db.commit()
    db.refresh(todo_item)
    return todo_item
@app.delete("/list/{id}")
def delete_item(id:int,db:Session=Depends(get_db)):
   result = db.query(models.TodoItem).filter(models.TodoItem.id==id).first()
   if not result:
    raise HTTPException(status_code=404, detail="item not found")
   db.delete(result)
   db.commit()
   return result