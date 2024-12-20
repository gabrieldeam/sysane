from app.utils.hashing import hash_password, verify_password
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate

def create_user(db: Session, user: UserCreate):
    hashed_pw = hash_password(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        company_name=user.company_name,
        company_size=user.company_size,
        work_area=user.work_area,
        department=user.department,
        hashed_password=hashed_pw,
        accepted_privacy_policy=user.accepted_privacy_policy,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str):
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user
