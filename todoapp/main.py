from typing import Union
from fastapi import FastAPI

from fastapi import HTTPException

from pydantic import BaseModel


app = FastAPI()

class Todolist(BaseModel):
    id: int
    task: str
    user:str

Todo:list[Todolist]=[
    Todolist(id=1 , user="refad" , task="test"),
]


@app.get("/list")
def get_items() -> list[Todolist]:
    return Todo
@app.post("/list")
def add_item(item: Todolist) -> Todolist:
    Todo.append(item)
    return item
@app.put("/list")
def update_item(item:Todolist) -> Todolist:
    for i in Todo:
        if  i.id== item.id:
            i.user=item.user
            i.task=item.task
            return i
    raise HTTPException(status_code=404, detail="item not found")
@app.delete("/list/{id}")
def delete_item(id:int) -> None:
    for i in Todo:
        if i.id==id:
            Todo.remove(i)
            return 
    raise HTTPException(status_code=404, detail="item not found")
