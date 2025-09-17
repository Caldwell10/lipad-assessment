from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .db import Base

# users table
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, nullable=False)
    phone_number = Column(String, nullable=False)
    loans = relationship("LoanRequest", back_populates="user", cascade="all, delete-orphan")

# loan requests table
class LoanRequest(Base):
    __tablename__ = "loan_requests"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable = False, index=True)
    amount = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="PENDING") # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    user = relationship("User", back_populates="loans")

# API logs table
class APILog(Base):
    __tablename__ = "api_logs"
    id = Column(Integer, primary_key=True)
    direction = Column(String, nullable=False)  # incoming or outgoing
    url = Column(String, nullable=False)
    payload = Column(String, nullable=True)
    status_code = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


    