#from fastapi import APIRouter
from app.backend.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.models.task import Task

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.routers.schemas import CreateUser, UpdateUser
from sqlalchemy import insert, select, update, delete
from slugify import slugify


router = APIRouter(prefix='/user', tags=['user'])

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    firstname = Column(String)
    lastname = Column(Integer, default=0)
    age = Column(Integer)
    slug = Column(String, unique=True, index=True)
    tasks = relationship('Task', back_populates='user')

# from sqlalchemy.schema import CreateTable
# print(CreateTable(Task.__table__))
# print(CreateTable(User.__table__))

@router.get('/')
async def all_users(db: Annotated[Session, Depends(get_db)]):
    return db.scalars(select(User)).all()

@router.get('/tuser_id')
async def user_by_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    users = db.scalar(select(User).where(User.id == user_id))
    if users:
        return users
    raise HTTPException(status_code=404, detail='User was not found')

@router.post('/create')
async def create_user(db: Annotated[Session, Depends(get_db)], create_category: CreateUser):
    db.execute(insert(User).values(username=create_category.username,
                                   firstname=create_category.firstname,
                                   lastname=create_category.lastname,
                                   age=create_category.age,
                                   slug=slugify(create_category.username)))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }

@router.put('/update')
async def update_user(db: Annotated[Session, Depends(get_db)], user_id: int, update_category: UpdateUser):
    users = db.scalar(select(User).where(User.id == user_id))
    if users is None:
        raise HTTPException(status_code=404, detail='User was not found')

    db.execute(update(User).where(User.id == user_id).values(firstname=update_category.firstname,
                                                             lastname=update_category.lastname,
                                                             age=update_category.age))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.delete('delete')
async def delete_user(db: Annotated[Session, Depends(get_db)], user_id: int):
    users = db.scalar(select(User).where(User.id == user_id))
    tasks = db.scalars(select(Task).where(Task.user_id==user_id)).all
    if users is None:
        raise HTTPException(status_code=404, detail='User was not found')
    db.execute(delete(User).where(User.id == user_id))

    if tasks:
        db.execute(delete(Task).where(Task.user_id==user_id))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.get('/user_id/tasks')
async def tasks_by_users_id(db: Annotated[Session, Depends(get_db)], user_id: int):
    tasks = db.scalars(select(Task).where(Task.user_id==user_id)).all()
    return tasks
