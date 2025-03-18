# filepath: /c:/JCPG-summarizer/Backend/app/routes/user_routes.py
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.schemas import UserCreate
from app.utils.auth import create_access_token, hash_password, verify_password
from fastapi.security import OAuth2PasswordBearer

router = APIRouter()


@router.post("/register/")
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"id": new_user.id, "email": new_user.email}

@router.post("/login/")
async def authenticate_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email or password")
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid email or password")
    access_token = create_access_token(data={"sub": db_user.email})
    return {
            "email": db_user.email,
            "access_token": access_token,
            "token_type": "bearer"
        }