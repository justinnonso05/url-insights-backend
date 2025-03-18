import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)

    # Define relationship to summaries
    summaries = relationship("Summary", back_populates="user")

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), unique=True, index=True)
    url = Column(String, index=True)
    content = Column(String)
    user_id = Column(String(36), ForeignKey('users.id'), index=True)

    # Define relationship to user
    user = relationship("User", back_populates="summaries")