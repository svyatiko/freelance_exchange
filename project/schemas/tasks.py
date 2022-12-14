import datetime
from datetime import date
from typing import Optional

from pydantic import BaseModel


# shared properties
class TaskBase(BaseModel):
    title: Optional[str] = None
    sphere: Optional[str] = None
    stack: Optional[str] = None
    git_link: Optional[str] = None
    description: Optional[str] = None
    payment_type: Optional[str] = None
    price: Optional[str] = None


# this scheme will be used to validate data while creating a task
class TaskCreate(TaskBase):
    title: str
    sphere: str
    stack: str
    git_link: str
    description: str
    payment_type: str
    price: str
    task_status: str = "dev not selected"


# this will be used to format the response to not to have id, owner_id
class ShowTask(TaskBase):
    title: str
    company: str
    company_url: Optional[str]
    location: str
    date_posted: date
    description: Optional[str]

    class Config:
        orm_mode = True


class CreateTaskMsg(BaseModel):
    task_id: int
    dev_id: int
    msg: str
    msg_time: date = datetime.datetime.now()
