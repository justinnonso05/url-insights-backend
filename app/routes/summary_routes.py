from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Header
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Summary, User
from app.services import summarizer
from app.utils.auth import decode_access_token
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, HTTPBasic, HTTPBasicCredentials
import logging
import json

security = HTTPBearer(auto_error=False)  # Make authentication optional
router = APIRouter()

@router.post("/summarize")
async def summarize(
    url: str,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
):
    user = None

    # Authenticate user
    if credentials:
        try:
            token = credentials.credentials
            payload = decode_access_token(token)
            user_email = payload.get("sub")

            if user_email:
                user = db.query(User).filter(User.email == user_email).first()
        except Exception as e:
            logging.warning(f"Authentication error: {str(e)}")

    # Generate summary
    summarized_text = await summarizer.summarize_text(url)  # likely returns a dict

    # Store summary only if user is authenticated
    if user:
        new_summary = Summary(
            url=url, 
            content=json.dumps(summarized_text),  # ✅ Convert dict to JSON before storing
            user_id=user.id
        )
        db.add(new_summary)
        db.commit()
        db.refresh(new_summary)

        return {
            "id": new_summary.id,
            "url": new_summary.url,
            "summary": summarized_text,  # Keep this as a dict in the response
            "saved": True
        }

    # For anonymous users, return the summary without saving
    return {
        "url": url,
        "summary": summarized_text,
        "saved": False
    }


@router.get("/my-summaries")
async def my_summaries(
    credentials: HTTPAuthorizationCredentials = Depends(security), 
    db: Session = Depends(get_db)
):
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
        
    token = credentials.credentials
    payload = decode_access_token(token)
    user_email = payload.get("sub")
    
    if not user_email:
        raise HTTPException(status_code=401, detail="Unauthorized")
        
    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    summaries = db.query(Summary).filter(Summary.user_id == user.id).all()
    return summaries