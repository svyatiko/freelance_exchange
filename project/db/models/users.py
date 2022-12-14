from sqlalchemy import Boolean, Column, Date, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from db.base_class import Base


class User_Account(Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    email = Column(String, nullable=False)
    regist_date = Column(Date)
    rate = Column(Integer, nullable=False)
    user_role = Column(String, nullable=False)


class Activity_log(Base):
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user_account.id"))
    user_name = Column(String, nullable=False)
    user_role = Column(String, nullable=False)
    activity_type = Column(String, nullable=False)
    operation_value = Column(String, nullable=False)
    activity_date = Column(Date)
    additional_info = Column(String, nullable=False)


class Rate_Statistic(Base):
    id = Column(Integer, primary_key=True, index=True)
    dev_id = Column(Integer, ForeignKey("user_account.id"))
    customer_id = Column(Integer, ForeignKey("user_account.id"))
    customer_msg = Column(String, nullable=False)
    mark = Column(Integer, nullable=False)
