from fastapi import APIRouter, Depends, HTTPException,status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from app import models, schemas,utils
from app.database import get_db
from sqlalchemy.orm import Session

router=APIRouter(
    tags=["Authentication"]
)

@router.post("/login")

def login(user_credentials:OAuth2PasswordRequestForm=Depends(), db:Session=Depends(get_db)):

    user=db.query(models.User).filter(models.User.username == user_credentials.username).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            details="Invalid Crdentials"
        )
    
    if not utils.verify(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Invalid Credentials"
        )
    
    access_token=utils.create_jwt_token(data={"user_id":user.id})

    return {"access_token":access_token, "token_type":"bearer"}