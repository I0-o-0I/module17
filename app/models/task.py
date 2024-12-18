import app.models
from app.backend.db import Base
from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.models import *

from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from app.backend.db_depends import get_db
from typing import Annotated
from app.routers.schemas import CreateTask, UpdateTask
from sqlalchemy import insert, select, update, delete
from slugify import slugify


router = APIRouter(prefix='/task', tags=['task'])

class Task(Base):
    __tablename__ = 'tasks'
    __table_args__ = {'extend_existing': True}
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    priority = Column(Integer, default=0)
    completed = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    slug = Column(String, unique=True,index=True)
    user = relationship('User', back_populates='tasks')

# from sqlalchemy.schema import CreateTable
# print(CreateTable(Task.__table__))
# print(CreateTable(User.__table__))


@router.get('/')
async def all_tass(db: Annotated[Session, Depends(get_db)]):
    return db.scalars(select(Task)).all()


@router.get('/task_id')
async def task_by_id(db: Annotated[Session, Depends(get_db)], task_id: int):
    tasks = db.scalar(select(Task).where(Task.id == task_id))
    if tasks:
        return tasks
    raise HTTPException(status_code=404, detail='Task was not found')

@router.post('/create')
async def create_task(db: Annotated[Session, Depends(get_db)], user_id: int, create_category: CreateTask):
    users = db.scalar(select(app.models.User).where(app.models.User.id == user_id))
    if users:
        db.execute(insert(Task).values(title=create_category.title,
                                       content=create_category.content,
                                       priority=create_category.priority,
                                       user_id=user_id,
                                       slug=slugify(create_category.title)))
        db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }

    raise HTTPException(status_code=404, detail='User was not found')


@router.put('/update')
async def update_task(db: Annotated[Session, Depends(get_db)], task_id: int, update_category: UpdateTask):
    tasks = db.scalar(select(Task).where(Task.id == task_id))
    if tasks is None:
        raise HTTPException(status_code=404, detail='User was not found')

    db.execute(update(Task).where(Task.id == task_id).values(title=update_category.title,
                                   content=update_category.content,
                                   priority=update_category.priority))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.delete('delete')
async def delete_task(db: Annotated[Session, Depends(get_db)], task_id: int):
    tasks = db.scalar(select(Task).where(Task.id == task_id))
    if tasks is None:
        raise HTTPException(status_code=404, detail='Task was not found')

    db.execute(delete(Task).where(Task.id == task_id))
    db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }

