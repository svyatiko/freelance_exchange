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


def update_user_password_by_id(id: int, user: UserCreate, db: Session):
    existing_user = db.query(User_Account).filter(User_Account.id == id)
    user.__dict__.update(hashed_password=Hasher.get_password_hash(user.password))
    delattr(user, "password")
    if not existing_user.first():
        return 0
    existing_user.update(user.__dict__)
    db.commit()
    return 1
