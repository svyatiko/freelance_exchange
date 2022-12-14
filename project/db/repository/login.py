from sqlalchemy.orm import Session

from db.models.users import User_Account


def get_user(username: str, db: Session):
    user = db.query(User_Account).filter(User_Account.email == username).first()
    return user
