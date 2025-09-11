from sqlalchemy.orm import Session
from fastapi import Depends,HTTPException
from models.user import User, RoleEnum
from core.security import hash_password


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, email: str,name:str, mobile: int, verified,verification_token,password: str, role: RoleEnum = RoleEnum.user):
    db_user = User(
        email=email,
        name=name,
        mobile=mobile,
        verified=verified,
        verification_token=verification_token,
        hashed_password=hash_password(password),
        role=role,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user




