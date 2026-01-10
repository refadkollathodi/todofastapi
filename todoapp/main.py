from typing import Union
from fastapi import FastAPI
from fastapi import HTTPException
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from datetime import datetime,timedelta
from jose import JWTError,jwt
from passlib.context import CryptContext

import models
import logging
from database import engine,SessionLocal
from sqlalchemy.orm import Session
from fastapi import Depends,status

SECRET_KEY="09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3ef"
ALGORITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30

#testing

app = FastAPI()
models.Base.metadata.create_all(bind=engine)


def get_user(db:Session,username:str):
   return db.query(models.User).filter(models.User.username==username).first()

class Token(BaseModel):
   access_token:str
   token_type:str
class TokenData(BaseModel):
   username:str|None = None
class User(BaseModel):
   username:str
   disabled:bool|None=None
class UserInDB(User):
   hashed_password:str
class UserRegister(BaseModel):
    username: str
    password: str
    disabled: bool = False

password_context=CryptContext(schemes=["pbkdf2_sha256"],deprecated="auto")
OAuth2_scheme=OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password,hashed_password):
   return password_context.verify(plain_password,hashed_password)
def get_password_hash(password):
   return password_context.hash(password)


class Todolist(BaseModel):
    task: str
    user:str

def get_db():
    db=SessionLocal()
    try:
        yield db
    finally:
        db.close()
def authenticate_user(db:Session,username:str,password:str):
   user=get_user(db,username)
   if not user:
      return False
   if not verify_password(password,user.hashed_password):
      return False
   return user
def create_access_token(data:dict,expires_delta:timedelta=None):
   to_encode=data.copy()
   if expires_delta:
      expires_delta=datetime.utcnow()+expires_delta
   else:
      expires_delta=datetime.utcnow()+timedelta(minutes=15)
   to_encode.update({"exp":expires_delta})
   encode_jwt=jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
   return encode_jwt
   
async def get_current_user(token:str=Depends(OAuth2_scheme),db:Session=Depends(get_db)):
    credentials_exception=HTTPException(
       status_code=status.HTTP_401_UNAUTHORIZED,
       detail="Could not validate credentials",
       headers={"WWW-Authenticate":"Bearer"},

    )
    try:
       payload=jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
       username:str=payload.get("sub")
       if username is None:
          raise credentials_exception
       token_data=TokenData(username=username)
    except JWTError:
       raise credentials_exception
    user=get_user(db,username=token_data.username)
    if user is None:
       raise credentials_exception
    return user

async def get_current_active_user(current_user:User=Depends(get_current_user)):
   if current_user.disabled:
      raise HTTPException(status_code=400,detail="Inactive user")
   return current_user

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(asctime)s | %(name)s | %(message)s"
)
logger = logging.getLogger("todo-app")


@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(),
                                 db:Session=Depends(get_db)):
    user=authenticate_user(db,form_data.username,form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/user/me",response_model=User)
async def read_users_me(current_user:User=Depends(get_current_active_user)):
   return current_user
@app.get("/user/me/items")
async def read_own_items(current_user:User=Depends(get_current_active_user)):
   return [{"itme_id":1,"owner":current_user.username}]
@app.post("/register",status_code=status.HTTP_201_CREATED)
def register_user(user:UserRegister,db:Session=Depends(get_db)):
    exsiting_user=get_user(db,user.username)
    if exsiting_user:
       raise HTTPException(status_code=400,detail="username already exist")
    hashed_password=get_password_hash(user.password)
    new_user=models.User(
       username=user.username,
       hashed_password=hashed_password,
       disabled=user.disabled
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message":"user created successfully","username":new_user.username}


@app.get("/list/{user}")
def get_items_user(user:str,db:Session=Depends(get_db),current_user:User=Depends(get_current_active_user)):
   result = db.query(models.TodoItem).filter(models.TodoItem.user==user).all()
   if not result:
    raise HTTPException(status_code=404, detail="item not found")
   return result
    


@app.get("/list")
def get_items(db:Session=Depends(get_db),current_user:User=Depends(get_current_active_user)):
   return db.query(models.TodoItem).all()

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