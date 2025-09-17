
import json

from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from .db import Base, engine, get_db
from .models import User, LoanRequest
from .schemas import UserCreate, UserOut, LoanCreate, LoanOut, WebhookIn
from .services import save_api_log, touch_updated_at

app = FastAPI()

# create tables on start-up
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

""" 
User Endpoint
"""

@app.post("/users", response_model=UserOut)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    # check if email already exists
    exists = db.scalar(
        select(func.count()).select_from(User).where(User.email == payload.email)
    )
    if exists:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user = User(
        name=payload.name,
        email=payload.email,
        phone_number=payload.phone_number
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

"""
Loan Request Endpoints
"""
@app.post("/loan-requests", response_model=LoanOut)
async def create_loan_request(payload: LoanCreate, request: Request, db: Session = Depends(get_db)):
    # check if user exists
    user: Optional[User] = db.get(User, payload.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # validate amount
    amount = float(payload.amount)
    if not (0 < amount < 1_000_000):
        raise HTTPException(status_code=400, detail="Invalid amount. Amount must be between 0 and 1,000,000")
    
    # reject duplicate pending for this user
    has_pending = db.scalar(
        select(func.count()).select_from(LoanRequest)
        .where(LoanRequest.user_id == payload.user_id, LoanRequest.status == "PENDING")
    )
    if has_pending:
        raise HTTPException(status_code=400, detail="User already has a pending loan request")
    
    # create loan request
    loan = LoanRequest(
        user_id=payload.user_id,
        amount=amount,
        status="PENDING"
    )
    db.add(loan)
    db.commit()
    db.refresh(loan)

    # send to mock credit scoring API
    outgoing = {
        "loan_id": loan.id,
        "amount": loan.amount,
        "user":{"name": user.name,"email": user.email },
        "callback_url" : str(request.base_url).rstrip("/") + "/webhooks/credit-score"   
    }

    # set api log status to 0 
    save_api_log(db, direction="OUTGOING", url = "https://mock-credit-score.com/api/score", payload=outgoing, status_code=0)
    print(" Outgoing -> mock-credit-api", json.dumps(outgoing))

    return _loan_to_out(loan)

# fetch a single loan request by id
@app.get("/loan-requests/{loan_id}", response_model=LoanOut)
def get_loan_request(loan_id: int, db: Session = Depends(get_db)):
    loan = db.get(LoanRequest, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return _loan_to_out(loan)


"""
Webhook Endpoint
"""
@app.post("/webhook/credit-score")
def credit_score_webhook(payload: WebhookIn, request: Request, db: Session = Depends(get_db)):
    # Log incoming webhook
    save_api_log(db, direction="INCOMING", url = str(request.url), payload=payload.model_dump(), status_code=200)

    # Validate status value
    if payload.status not in ("PENDING", "APPROVED", "REJECTED"):
        raise HTTPException(status_code=400, detail="Invalid status value")
    
    # update the loan
    loan = db.get(LoanRequest, payload.loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    # apply updates
    loan.status = payload.status               
    loan.reason = payload.reason               
    touch_updated_at(loan)

    # commit changes
    db.commit()

    return {"message": "Loan updated", "loan_id": loan.id, "status": loan.status}

"""
Helper functions
"""

# convert LoanRequest model to LoanOut schema
def _loan_to_out(loan: LoanRequest) -> LoanOut:
    return LoanOut(
        id=loan.id,
        user_id=loan.user_id,
        amount=loan.amount,
        status=loan.status,
        created_at=loan.created_at.isoformat(),
        updated_at=loan.updated_at.isoformat()
    )

# format date object to a a string 
def _dt(d: datetime) -> str:
    return d.strftime('%Y-%m-%dT%H:%M:%SZ')



