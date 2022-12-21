from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.base_class import Base


class Task(Base):
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("user_account.id"))
    dev_id = Column(Integer, ForeignKey("user_account.id"))
    title = Column(String, nullable=False)
    sphere = Column(String, nullable=False)
    stack = Column(String, nullable=False)
    description = Column(String, nullable=False)
    payment_type = Column(String, nullable=False)
    price = Column(Integer, nullable=False)
    git_link = Column(String, nullable=False)
    task_status = Column(String, nullable=False)


class Task_msg(Base):
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("task.id"))
    dev_id = Column(Integer, ForeignKey("user_account.id"))
    dev_username = Column(String, nullable=False)
    msg = Column(String, nullable=False)
    msg_time = Column(Date)


class Github_Commit(Base):
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("task.id"))
    com_title = Column(String, nullable=False)
    com_date = Column(String, nullable=False)
    com_link = Column(String, nullable=False)


class Hour_Statistic(Base):
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("task.id"))
    hour = Column(Integer, nullable=False)
    check_date = Column(Date)
