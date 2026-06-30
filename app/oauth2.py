from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from app import models, utils
from app.database import get_db
from app.config import settings

# This tells FastAPI where the login endpoint is, so it can automatically
# wire up the "Authorize" button in the Swagger UI docs.
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """
    This function intercepts the request, grabs the JWT token from the header,
    decodes it, and returns the User object from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Decode the token using our secret key
        payload = jwt.decode(token, settings.secret_key, algorithms=[utils.ALGORITHM])
        
        # 2. Extract the user_id we embedded earlier
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
            
    except jwt.PyJWTError: # Catch expired or tampered tokens
        raise credentials_exception
        
    # 3. Fetch the actual user from the database
    user = db.query(models.User).filter(models.User.id == user_id).first()
    
    if user is None:
        raise credentials_exception
        
    return user