from datetime import date

from sqlalchemy.orm import Session

from core.hashing import Hasher
from db.models.users import User_Account
from schemas.users import UserCreate


def create_new_user(user: UserCreate, db: Session):
    user = User_Account(
        username=user.username,
        email=user.email,
        regist_date=date.today(),
        rate=0,
        hashed_password=Hasher.get_password_hash(user.password),
        user_role=user.user_role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
