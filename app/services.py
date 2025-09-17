import json 
from datetime import datetime
from sqlalchemy.orm import Session
from .models import APILog

# confirm that requests and responses are successfully logged
def save_api_log(db: Session, *, direction:str, url:str, payload:dict | None, status_code:int):
    db.add(APILog(
        direction=direction,
        url=url,
        payload = json.dumps(payload) if payload is not None else None,
        status_code=status_code,
        ))
    db.commit()

# reflect last update time on loan requests
def touch_updated_at(obj):
    if hasattr(obj, "updated_at"):
        setattr(obj, "updated_at", datetime.utcnow())